import json
import hjson  # https://github.com/hjson/hjson-py
import regex
import logging
from typing import Any, Dict, Generator, Hashable, Iterable, Iterator, Union
from shortest_common_supersequence import shortest_common_supersequence, longest_common_subsequence


# functools.reduce may exceed maximum recursion depth when function is a generator, so let's force iteration
def reduce_generator(generator_func: Generator[Any, None, None], iterable: Iterable[Any]) -> list:
    iterator = iter(iterable)
    accumulated = next(iterator)
    for element in iterator:
        accumulated = list(generator_func(accumulated, element))
    return accumulated

def standardize(dicts: Iterable[dict]) -> Iterator[dict]:
	list_of_dicts = list(dicts)

	all_keys = list(reduce_generator(shortest_common_supersequence, (d.keys() for d in list_of_dicts)))

	logging.debug(all_keys)

	template = {k: None for k in all_keys}

	# Yield each dictionary with the missing keys added with None as value
	for dic in list_of_dicts:
		yield {**template, **dic}


def dict_of_dicts_2_iter_of_dicts(dict_of_dicts: Dict[Hashable, dict], key_name: str) -> Iterator[dict]:
	for k, v in dict_of_dicts.items():
		yield {key_name: k, **v}

# Maybe when pyjsparser gets extended support for ECMAScript 6 I can drop the regex in favor of a proper parser.
def extract_json_from_ts(ts_str: str) -> Union[str, int, float, bool, None, list, Dict[str, Any]]:
	trimmed_str = ''.join(ts_str.split(' = ', 1)[1:]).rsplit('}', 1)[0] + '}'
	functionless_str = regex.sub(
		r'^(\s+)[^\d\W]\w*\s*\(.*?\)\s*\{(?:\s+?|.+?\n\1)\},?',
		'',
		trimmed_str,
		flags=regex.DOTALL|regex.MULTILINE|regex.UNICODE
	)
	return hjson.loads(functionless_str)


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)s, %(lineno)d] %(levelname)s: %(message)s')

	for filename in ('typechart', 'abilities', 'text/abilities', 'items', 'text/items', 'moves', 'text/moves', 'pokedex', 'text/pokedex', 'learnsets'):
		with open(f'./pokemon-showdown/data/{filename}.ts', 'r') as f:
			json_dict = extract_json_from_ts(f.read())

		# Generate list of dicts from dict of dicts
		dicts = list(dict_of_dicts_2_iter_of_dicts(json_dict, 'alias'))

		logging.debug(list(reduce_generator(longest_common_subsequence, (d.keys() for d in dicts))))

		with open(f'./json/{filename}.json', 'w', encoding='utf-8') as f:
			#json.dump(list(standardize(dicts)), f, ensure_ascii=False, indent='\t')
			json.dump(dicts, f, ensure_ascii=False, indent='\t')
