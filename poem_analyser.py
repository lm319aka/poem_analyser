from pylabeador import syllabify_with_details, syllabify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Constants:
    """
    Groups constants for better organization.
    """
    VOWELS = ["a", "e", "i", "o", "u"]
    VOWELS_WITH_ACCENT = ["á", "é", "í", "ó", "ú"]
    SWITCH = {a: b for a, b in zip(VOWELS_WITH_ACCENT, VOWELS)}
    OPEN_VOWELS = ["a", "e", "o", "á", "é", "ó", "í", "ú"]
    UNION_LETTERS_END = ["a", "e", "i", "o", "u", "y"] + VOWELS_WITH_ACCENT
    UNION_LETTERS_START = UNION_LETTERS_END + ["h"]
    CHARS_TO_DELETE = [".", ";", ",", "!", "¡", "?", "¿", ":"]
    UPPER_CASE_ALPHABET = ["-"] + [format(i, "c") for i in range(65, 91)]
    LOWER_CASE_ALPHABET = ["-"] + [format(i, "c") for i in range(97, 123)]
    EQUIV = {1: "aguda", 2: "llana", 3: "esdrujula", 4: "sobresdrújula"}
    CONVERT = {True: 1, False: 0}


def delete_clones(any_list: list) -> list:
    """
    Removes duplicate elements from a list efficiently using sets.

    :param any_list: The input list.
    :return: A new list with only unique elements, preserving the original order as much as possible.
    """
    return list(dict.fromkeys(any_list))


class Word:
    """
    Represents a word and its properties, such as syllables, tonic syllable, and union characteristics.
    """

    def __init__(self, word: str):
        """
        Initializes a Word object.

        :param word: The word to be analyzed.
        """
        self.word = word
        self.length = len(word)
        self.syllables = syllabify(word)
        self.last_syllable_rhymes = [self.syllables[-1]]
        self.number_of_syllables = len(self.syllables)
        try:
            self.tonic_silable_codec = self.find_tonic()
            self.tonic_silable = Constants.EQUIV[self.tonic_silable_codec]
        except ValueError as e:
            logging.error(f"Error finding tonic syllable for word '{word}': {e}")
            self.tonic_silable_codec = None
            self.tonic_silable = None
        self.start, self.end = self.union()

    def find_tonic(self) -> int:
        """
        Finds the tonic (stressed) syllable in the word.

        :return: The index of the tonic syllable.
        :raises ValueError: If no tonic syllable is found.
        """
        syllabified = syllabify_with_details(self.word)
        accent_index: int = 0
        for cn, syllable in enumerate(syllabified.syllables):
            if syllable.stressed:
                accent_index = len(self.syllables) - cn
                break
        if accent_index == 0:
            raise ValueError(f"No tonic syllable found in '{self.word}'")
        elif 0 < accent_index < 4:
            return accent_index
        else:
            return 4

    def union(self) -> tuple[bool, bool]:
        """
        Checks if the word starts or ends with a union letter.

        :return: A tuple indicating whether the word starts and ends with a union letter.
        """
        start = self.word[0] in Constants.UNION_LETTERS_START
        end = self.word[-1] in Constants.UNION_LETTERS_END
        return start, end


class Rhyme:
    """
    Represents a rhyme and its properties, such as syllables, rhyme type, and arte type.
    """

    def __init__(self, rhyme: str):
        """
        Initializes a Rhyme object.

        :param rhyme: The rhyme string to be analyzed.
        """
        self.original_rhyme = rhyme
        self.refined_rhyme = "".join(ch for ch in rhyme if ch not in Constants.CHARS_TO_DELETE)
        self.part_list = self.refined_rhyme.split(" ")
        self.last_word = self.part_list[-1]
        self.syllables = self.cl_syllables()
        self.arte = self.type_arte()
        self.complete_section, self.vocal_section = self.rhyme_types()

    def cl_syllables(self) -> int:
        """
        Calculates the number of syllables in the rhyme, considering unions.

        :return: The total number of syllables.
        """
        data_words = [Word(i) for i in self.part_list]
        data_unions = [Constants.CONVERT[w.start] for w in data_words] + [Constants.CONVERT[w.end] for w in data_words]
        data_unions = data_unions[1:-1]
        aux = [[data_unions[c - 1], i] for c, i in enumerate(data_unions) if c % 2 == 1]

        total_syllables = [w.number_of_syllables for w in data_words]
        unions = sum(1 for n, m in aux if n and m)
        return sum(total_syllables) - unions

    def type_arte(self) -> bool:
        """
        Determines the type of arte (major or minor) based on the number of syllables.

        :return: True if the number of syllables is greater than 8 (arte mayor), False otherwise (arte menor).
        """
        return self.syllables > 8

    def rhyme_types(self) -> tuple[str, list[str]]:
        """
        Determines the rhyme type based on the last word's syllables.

        :return: A tuple containing the last two syllables of the last word and a list of vowels in those syllables.
        """
        lword = Word(self.last_word)
        lword_syllables = lword.syllables
        if len(lword_syllables) == 1:
            return self.last_word, [i for i in self.last_word if i in Constants.VOWELS + Constants.VOWELS_WITH_ACCENT]
        else:
            part = "".join(lword_syllables[-2:])
            return part, [i for i in part if i in Constants.VOWELS + Constants.VOWELS_WITH_ACCENT]


class Poem:
    """
    Represents a poem and its properties, such as syllables, rhyme scheme, and poem type.
    """

    def __init__(self, poem: str):
        """
        Initializes a Poem object.

        :param poem: The poem string to be analyzed.
        """
        self.poem = poem.lower()
        self.syllables, self.scheme, self.verses = self.classify()
        self.poem_type = self.rhyme_type()

    def rhyme_type(self) -> str:
        """
        Determines the type of poem based on the rhyme scheme and number of verses.

        :return: The type of poem as a string.
        """
        str_scheme = "".join(self.scheme)
        num_verses = len(self.verses)

        match num_verses:
            case 2:
                return "pareado"
            case 3:
                match str_scheme:
                    case "ABA":
                        return "terceto"
                    case "aba":
                        return "tercerilla"
                    case _:
                        return "Unknown"
            case 4:
                match str_scheme:
                    case "ABBA":
                        return "cuarteto"
                    case "ABAB":
                        return "serventesio"
                    case "abba":
                        return "redondilla"
                    case "abab":
                        return "cuarteta"
                    case "-a-a":
                        return "serventesio"
                    case "AAAA":
                        if self.syllables.count(14) == 4:
                            return "cuaderna via"
                        else:
                            return "Unknown"
                    case _:
                        return "Unknown"
            case 5:
                quintilla_cases = ["ababa", "abaab", "abbab", "aabab", "aabba"]
                quinteto_cases = [i.upper() for i in quintilla_cases]

                if str_scheme in quintilla_cases:
                    return "quintilla"
                elif str_scheme in quinteto_cases:
                    return "quinteto"
                elif self.verses == ["7a", "11B", "7a", "7b", "11B"]:
                    return "lira"
                else:
                    return "Unknown"
            case 6:
                match str_scheme:
                    case "ABABCC":
                        return "sexta rima"
                    case "AABBCC":
                        return "sextilla"
                    case _:
                        return "Unknown"
            case 8:
                match str_scheme:
                    case "ABABABCC":
                        return "octava real"
                    case "-aab-ccb":
                        return "octavilla"
                    case "abbaaccddc":
                        return "décima espinela"
                    case _:
                        return "Unknown"
            case 10:
                match str_scheme:
                    case "abbaaccddc":
                        return "décima espinela"
                    case _:
                        return "Unknown"
            case 14:
                soneto_cases = ["ABBAABBACDCDCD", "ABBAABBACDECDE", "ABBAABBACDEDCE"]
                if str_scheme in soneto_cases:
                    return "soneto"
                else:
                    return "Unknown"
            case _:
                if str_scheme.count("-") == len(str_scheme):
                    return "verso libre"
                else:
                    return "Unknown"

    def classify(self) -> tuple[list[int], list[str], list[str]]:
        """
        Classifies the poem by analyzing its rhymes and syllables.

        :return: A tuple containing lists of syllables, rhyme schemes, and verses.
        """
        poem_parts = [part for part in self.poem.split("\n") if part]
        logging.info(f"Poem parts: {poem_parts}")
        data_poem = [Rhyme(i) for i in poem_parts]
        rhyme_matches = list()
        all_syllables = [i.syllables for i in data_poem]
        all_ends = [i.complete_section for i in data_poem]
        all_asonant_ends = []

        for end in all_ends:
            new_end = "".join(
                Constants.SWITCH.get(letter,
                                     letter) if letter in Constants.VOWELS + Constants.VOWELS_WITH_ACCENT else "*"
                for letter in end
            )
            all_asonant_ends.append(new_end)

        logging.info(f"Asonant ends: {all_asonant_ends}, Ends: {all_ends}")

        rhyme_count = 0
        scheme = []

        for cn, part in enumerate(all_ends):
            for rhm in rhyme_matches:
                logging.info(f"Scanning... rhm: {rhm}, part: {part}")
                if rhm in part:
                    logging.info("Yes, rhyme found...")
                    break
            else:
                for part2 in delete_clones(all_ends[cn + 1:]):
                    if part2[-1] == part[-1] and part2[-2] == part[-2]:
                        new_rhyme = ""
                        chain = list(reversed(part))
                        chain2 = list(reversed(part2))
                        for i in range(min(len(chain), len(chain2))):
                            if chain[i] == chain2[i]:
                                new_rhyme += chain[i]
                            else:
                                break
                        new_rhyme = "".join(reversed(new_rhyme))
                        rhyme_matches.append(new_rhyme)
                        rhyme_count += 1
                        break
                else:
                    actual_arhm = all_asonant_ends[cn]
                    if all_asonant_ends.count(actual_arhm) > 1:
                        logging.info(f"Asonant rhyme: {part}")
                    else:
                        for arhm in all_asonant_ends:
                            if arhm[-1] == actual_arhm[-1] and arhm[-2] == actual_arhm[-2]:
                                chain3 = list(reversed(arhm))
                                chain4 = list(reversed(actual_arhm))
                                _as = []
                                for i in range(min(len(chain3), len(chain4))):
                                    if chain3[i] == chain4[i]:
                                        _as.append(chain3[i])
                                    else:
                                        break
                                logging.info(_as)
                                break
                        logging.info(f"No rhyme: {part}")

        for chars in all_ends:
            for cmp in rhyme_matches:
                if cmp in chars:
                    scheme.append(rhyme_matches.index(cmp) + 1)
                    break
            else:
                scheme.append(0)

        scheme = [
            Constants.UPPER_CASE_ALPHABET[i] if all_syllables[c] > 8 else Constants.LOWER_CASE_ALPHABET[i]
            for c, i in enumerate(scheme)
        ]
        refined_scheme = [str(all_syllables[c]) + j for c, j in enumerate(scheme)]
        return all_syllables, scheme, refined_scheme


if __name__ == "__main__":
    pm = """
Bajo el cielo de la tarde,
el silencio se agranda.
Camina la brisa suave
por la tierra descansada.

El sol pinta de colores
los tejados y la calle,
mientras vuelan mis amores
en alas de un viejo valle.

La noche se va acercando,
y el sueño me acompaña,
con la luna iluminando
la quietud de la montaña.
"""
    obj2 = Poem(pm)
    print(obj2.verses, "\n", obj2.poem_type)
