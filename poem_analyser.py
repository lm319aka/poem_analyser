from pylabeador import syllabify_with_details, syllabify
# pyphen

vowels = ["a", "e", "i", "o", "u"]
vowels_with_accent = ["á", "é", "í", "ó", "ú"]
switch = {a: b for a, b in zip(vowels_with_accent, vowels)}
open_vowels = ["a", "e", "o", "á", "é", "ó", "í", "ú"]
union_letters_end = ["a", "e", "i", "o", "u", "y"] + vowels_with_accent
union_letters_start = union_letters_end + ["h"]
_del_words = [".", ";", ",", "!", "¡", "?", "¿", ":"]

bigs = ["-"] + [format(i, "c") for i in range(65, 91)]
smalls = ["-"] + [format(i, "c") for i in range(97, 123)]

# print(union_letters_end, union_letters_start)
equiv = {1: "aguda", 2: "llana", 3: "esdrujula", 4: "sobresdrújula"}
convert = {True: 1, False: 0}


def dclone(any_list):
    for i in any_list:
        while any_list.count(i) > 1:
            any_list.remove(i)
    return any_list


class Word:

    def __init__(self, word):
        self.word = word
        self.length = len(word)
        self.syllables = syllabify(word)  # pyphen.Pyphen(lang='es').inserted(word).split("-")
        self.last_syllable_rhymes = [self.syllables[-1]]
        self.number_of_syllables = len(self.syllables)
        self.tonic_silable_codec = self.find_tonic()
        self.tonic_silable = equiv[self.tonic_silable_codec]
        self.start, self.end = self.union()

    def find_tonic(self):
        syllabified = syllabify_with_details(self.word)
        accent_index: int = 0
        # print(syllabified, self.syllables, len(self.syllables))
        for cn, syllable in enumerate(syllabified.syllables):
            if syllable.stressed:
                accent_index = len(self.syllables) - cn
                # print(accent_index)
                break
        if accent_index == 0:
            raise ValueError("error: ?")
        elif 0 < accent_index < 4:
            return accent_index
        else:
            return 4

    def union(self):
        end = False
        start = False
        if self.word[0] in union_letters_start: start = True
        if self.word[-1] in union_letters_end: end = True
        return start, end


class Rhyme:

    def __init__(self, rhyme: str):
        self.original_rhyme = rhyme
        new = rhyme
        for ch in _del_words:
            new = new.replace(ch, "")
        self.refined_rhyme = new
        del new
        self.part_list = self.refined_rhyme.split(" ")
        self.last_word = self.part_list[-1]
        self.syllables = self.cl_syllables()
        self.arte = self.type_arte()
        self.complete_section, self.vocal_section = self.rhyme_types()

    def cl_syllables(self):
        data_words = [Word(i) for i in self.part_list]
        data_unions = list()
        for w in data_words:
            data_unions.append(convert[w.start])
            data_unions.append(convert[w.end])
        data_unions = data_unions[1:-1]
        aux = []
        for c, i in enumerate(data_unions):
            if c % 2 == 1:
                aux.append([data_unions[c - 1], i])

        total_syllables = [w.number_of_syllables for w in data_words]
        # print(data_unions, type(data_unions))
        unions = 0
        for n, m in aux:
            if n and m:
                unions += 1
        # print(aux, total_syllables)
        return sum(total_syllables) - unions

    def type_arte(self):
        if self.syllables > 8:
            return True
        else:
            return False

    def rhyme_types(self):
        lword = Word(self.last_word)
        lword_syllables = lword.syllables
        complete_list = vowels + vowels_with_accent
        if len(lword_syllables) == 1:
            return self.last_word, [i for i in self.last_word if i in complete_list]
        else:
            part = "".join(lword_syllables[-2:])
            return part, [i for i in part if i in complete_list]


class Poem:

    def __init__(self, poem: str):
        self.poem = poem.lower()
        self.syllables, self.scheme, self.verses = self.classify()
        self.poem_type = self.rhyme_type()

    def rhyme_type(self):
        str_scheme = "".join(self.scheme)
        match len(self.verses):

            case 2:
                return "pareado"

            case 3:
                match str_scheme:

                    case "ABA":
                        return "terceto"

                    case "aba":
                        if True:
                            return "tercerilla"
                        else:
                            return "soleá"

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
                if str_scheme == "ABABCC":
                    return "sexta rima"
                elif self.verses == ["8a", "8b", "4c", "8a", "8b", "4c"]:
                    return "copla de pie quebrado"
                else:
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

    def classify(self):
        poem_parts = self.poem.split("\n")
        if "" in poem_parts:
            poem_parts = [i for i in poem_parts if i]
        print(poem_parts)
        data_poem = [Rhyme(i) for i in poem_parts]
        # doesnt_rhyme = set()
        does_rhyme = list()
        all_syllables = [i.syllables for i in data_poem]
        all_ends = [i.complete_section for i in data_poem]
        all_asonant_ends = list()
        for end in all_ends:
            new = ""
            for letter in end:
                if letter in vowels:
                    new+=letter
                elif letter in vowels_with_accent:
                    new+=switch[letter]
                else:
                    new+="*"
            all_asonant_ends.append(new)
        print(all_asonant_ends, all_ends)
        acc = 0
        scheme = []
        for cn, part in enumerate(all_ends):
            for rhm in does_rhyme:
                print("scaning...", rhm, part)
                if rhm in part:
                    print("yes...")
                    break
            else:
                # print(f"in else {part}")
                for part2 in dclone(all_ends[cn + 1:]):
                    # print(part2)
                    if part2[-1] == part[-1] and part2[-2] == part[-2]:
                        # print("riman?:", part, part2)
                        new_rhyme = ""
                        if len(part2) > len(part):
                            chain = list(reversed(part))
                            chain2 = list(reversed(part2))
                        else:
                            chain = list(reversed(part2))
                            chain2 = list(reversed(part))
                        for i in range(len(chain)):
                            if chain[i] == chain2[i]:
                                new_rhyme += chain[i]
                            else:
                                break
                        new_rhyme = "".join(list(reversed(new_rhyme)))
                        does_rhyme.append(new_rhyme)
                        # print(new_rhyme)
                        acc += 1
                        break
                        # print(does_rhyme)
                    # else:
                        # pass
                        # break
                else:
                    """
                    for asonant_rhyme in all_asonant_ends:
                        a_new_one = True
                        for char in asonant_rhyme:
                            if asonant_rhyme.count(char) != part.count(char):
                                a_new_one = False
                                break
                        if a_new_one:
                            print("pues si rima:", part, asonant_rhyme)
                            # does_rhyme.append()
                            break
                    """
                    actual_arhm = all_asonant_ends[cn]
                    if all_asonant_ends.count(actual_arhm) > 1:
                        print("rima asonante:", part)
                    else:
                        # aux = list(reversed(actual_arhm))
                        for arhm in all_asonant_ends:
                            _as = list()
                            if arhm[-1] == actual_arhm[-1] and arhm[-2] == actual_arhm[-2]:
                                if len(arhm) > len(actual_arhm):
                                    chain3 = list(reversed(arhm))
                                    chain4 = list(reversed(actual_arhm))
                                else:
                                    chain3 = list(reversed(actual_arhm))
                                    chain4 = list(reversed(arhm))
                                for i in range(len(chain3)):
                                    if chain3[i] == chain4[i]:
                                        _as.append(chain3[i])
                                    else:
                                        break
                                print(_as)
                                break
                        print("no rima:", part)

        for chars in all_ends:
            for cmp in does_rhyme:
                if cmp in chars:
                    scheme.append(does_rhyme.index(cmp) + 1)
                    break
                else:
                    pass
            else:
                scheme.append(0)
        scheme = [bigs[i] if all_syllables[c] > 8 else smalls[i] for c, i in enumerate(scheme)]
        refined_scheme = [str(all_syllables[c]) + j for c, j in enumerate(scheme)]
        return all_syllables, scheme, refined_scheme


if __name__ == "__main__":
    # wr = Word("fácilmente")
    # print(wr.syllables, wr.tonic_silable_codec, wr.tonic_silable)
    pm = """
Tus ojos son luceros,
tus labios, de terciopelo,
y un amor como el que siento,
es imposible esconderlo.
"""

    """
    rm = "y órganos mi dolor sin instrumento"
    obj = Rhyme(rm)
    print(obj.original_rhyme, "\n",
          obj.refined_rhyme, "\n",
          obj.syllables, "\n",
          obj.arte, "\n",
          obj.complete_section, obj.vocal_section)

    """
    # print(Word("instrumento").syllables)
    obj2 = Poem(pm)
    print(obj2.verses, "\n", obj2.poem_type)
