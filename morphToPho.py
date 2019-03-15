import argparse
import os
import sys
import ast

PHONEME_DICT = {'confiamos': 'komfiamos', 'en': 'en', 'reunir': 'eunir', 'fuerzas': 'fwerTas', 'para': 'para', 'plantar': 'plantar', 'cara': 'kara', 
				'a': 'a', 'nuestros': 'nwestros', 'miedos': 'miedos', 'pero': 'pero', 'a': 'a', 'veces': 'beTes', 'y': 'i', 'sin': 'sin', 
				'querer': 'kerer', 'huimos': 'wimos', 
				'mi':'mi', 'propia':'propia', 'madre':'madre', 'intentó':'intento', 
				'matarme':'matarme', 'y':'i', 'como':'komo', 'me':'me', 
				'defendía':'defendia', 'mí':'mi', 'misma':'misma', 'que':'ke', 
				'había':'abia', 'un':'un', 'accidente':'akTidente'
				}


#old burned data
#this should be the output of the pause placement module. phrases, their start end time and pauses coming after
burned_phrase_structure = [  (['confiamos', 'en', 'reunir', 'fuerzas'], 0.0, 1.26, 0.12),
						(['para', 'plantar', 'cara', 'a', 'nuestros', 'miedos'], 1.38, 3.08, 0.31),
						(['pero', 'a', 'veces'], 3.39, 4.09, 0.06),
						(['y', 'sin', 'querer'], 4.15, 4.75, 0.98),
						(['huimos'], 5.73, 6.29, 0.0)
					]
burned_pho_list = ['k', 'o', 'm', 'f', 'i', 'a', 'm', 'o', 's', 'e', 'n', 'e', 'u', 'n', 'i', 'r', 'f', 'w', 'e', 'r', 'T', 'a', 's', '_', '_', 'p', 'a', 'r', 'a', 'p', 'l', 'a', 'n', 't', 'a', 'r', 'k', 'a', 'r', 'a', 'a', 'n', 'w', 'e', 's', 't', 'r', 'o', 's', 'm', 'i', 'e', 'd', 'o', 's', '_', '_', 'p', 'e', 'r', 'o', 'a', 'b', 'e', 'T', 'e', 's', '_', '_', 'i', 's', 'i', 'n', 'k', 'e', 'r', 'e', 'r', '_', '_', 'w', 'i', 'm', 'o', 's', '_', '_', '_', '_']

burned_pho_file = "heroes_s2_5_spa_aligned_spa0022.pho"
# OUTPUT_PHO_FILE = "heroes_s2_5_spa_aligned_spa0022_bent.pho"

# sentence_tokens = ['confiamos', 'en', 'reunir', 'fuerzas', '...' , 'para', 'plantar', 'cara', 'a', 'nuestros', 'miedos', ',', 'pero', 'a', 'veces', ',', 'y', 'sin', 'querer', ',', 'huimos', '.']


#for reading desired phrase structure
def parse_phrase_structure(phrase_stucture_file):
	phrase_structure = []
	with open(phrase_stucture_file, 'r') as f:
		for l in f:
			fields = l.split('\t')
			start_time = float(fields[0])
			end_time = float(fields[1])
			pause_after = float(fields[2])
			tokens = ast.literal_eval(fields[3])
			phrase_structure.append((tokens, start_time, end_time, pause_after))
	return phrase_structure


#pho file parser for reading default phoneme timings
def parse_pho(pho_file):
	phoneme_data = []
	with open(pho_file, 'r') as f:	
		for l in f:
			l_elems = l.split()
			if l_elems:
				if len(l_elems) == 2:
					phoneme_data.append((l_elems[0], l_elems[1], []))
				else:
					phoneme_data.append((l_elems[0], l_elems[1], l_elems[2:]))
	
	return phoneme_data

def get_phoneme_seq(phoneme_data):
	phoneme_list = []
	for phon_info in phoneme_data:
		phoneme_list.append(phon_info[0])
	return ''.join(phoneme_list)

def morpheme2phoneme(morpheme):
	try:
		return PHONEME_DICT[morpheme]
	except:
		print("not in dict") #TODO
		return 0

def get_duration_of_interval(phoneme_data, start_index, end_index):
	duration = 0
	for phoneme_info in phoneme_data[start_index: end_index]:
		duration += int(phoneme_info[1])
	return duration


def main(args):
	#read burned data
	#phrase_structure = burned_phrase_structure

	phrase_structure = parse_phrase_structure(args.phrase_structure_file)
	default_phoneme_data = parse_pho(args.default_pho_file)
	
	phoneme_seq = get_phoneme_seq(default_phoneme_data)

	print(phoneme_seq)

	desired_phrase_info = []
	phrase_boundaries = []
	phrase_durations = []
	phrase_pausings = []
	search_index = 0
	for phrase_tokens, start_time, end_time, pause_after in phrase_structure:

		beginning_index = search_index
		desired_phrase_duration = (end_time - start_time)* 1000	#desired duration
		desired_pause = int(pause_after * 1000)

		print("====================")
		print('beginning_index', beginning_index)
		for token_index, token in enumerate(phrase_tokens):
			phoneme_rep = morpheme2phoneme(token)
			
			word_begin = phoneme_seq.find(phoneme_rep, beginning_index)
			if token_index == 0:
				beginning_index = word_begin

			word_end = word_begin + len(phoneme_rep)
			word_length = word_end - word_begin
			print("%s %i - %i\t %s"%(token, word_begin, word_end, ''.join(phoneme_seq[word_begin: word_end])))
			search_index = word_end

		default_phrase_duration = get_duration_of_interval(default_phoneme_data, beginning_index, word_end)
		
		bend_ratio = default_phrase_duration/desired_phrase_duration

		desired_phrase_info.append(((beginning_index, word_end), bend_ratio, desired_pause))
		print("====================")
		print("interval", (beginning_index, word_end))
		print("ratio", bend_ratio)
		print("====================\n")

	print("--------------------====================--------------------")
	print(desired_phrase_info)


	#bend the durations of the phrases and form the desired phoneme data
	bent_phoneme_data = []
	for (beginning_index, end_index), bend_ratio, pause_after in desired_phrase_info:
		for phoneme_info in default_phoneme_data[beginning_index:end_index]:
			print(phoneme_info)
			new_duration = int(float(phoneme_info[1]) / bend_ratio)
			new_phoneme_info = (phoneme_info[0], '%i'%new_duration, phoneme_info[2])
			print(new_phoneme_info)
			bent_phoneme_data.append(new_phoneme_info)

		pause_info = ('_', pause_after, [])
		bent_phoneme_data.append(pause_info)
		print(pause_info)

	#write bent_phoneme_data to pho file
	with open(args.output_pho_file, 'w') as f:
		for i, phoneme_info in enumerate(bent_phoneme_data):
			f.write("%s\t%s\t%s"%(phoneme_info[0], phoneme_info[1], ' '.join(phoneme_info[2])))
			if not i == len(bent_phoneme_data):
				f.write("\n")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='PROG')
	parser.add_argument('-s', action='store', dest='phrase_structure_file')
	parser.add_argument('-p', action='store', dest='default_pho_file')
	parser.add_argument('-o', action='store', dest='output_pho_file')

	args = parser.parse_args()

	main(args)
