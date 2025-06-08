# Poem Analyzer

## Description

The Poem Analyzer is a Python tool that analyzes Spanish poems, providing insights into their structure, rhyme scheme, and type. It leverages the `pylabeador` library for syllabification and includes custom logic for rhyme detection and poem classification.

## Capabilities

*   **Syllable Counting:** Accurately counts syllables in each verse, considering unions between words.
*   **Rhyme Scheme Detection:** Identifies the rhyme scheme of the poem (e.g., ABBA, ABAB).
*   **Poem Type Classification:** Classifies the poem into various types such as sonnet, tercet, quartet, etc., based on the rhyme scheme and number of verses.
*   **Arte Type Determination:** Determines if a verse is arte mayor (more than 8 syllables) or arte menor (8 or fewer syllables).
*   **Unicode Support:** Handles Spanish words with accented vowels correctly.
*   **Logging:** Uses logging for debugging and monitoring.

## How It Works

The code is structured into several classes and functions:

*   **`Constants` Class:** A container for various constants used throughout the program, such as vowels, characters to delete, and equivalence mappings.
*   **`Word` Class:** Represents a word and its properties:
    *   `__init__`: Initializes a `Word` object, determines syllables, and finds the tonic syllable.
    *   `find_tonic`: Locates the tonic (stressed) syllable in the word using `pylabeador`.
    *   `union`: Checks if the word starts or ends with a union letter.
*   **`Rhyme` Class:** Represents a rhyme and its properties:
    *   `__init__`: Initializes a `Rhyme` object, refines the rhyme string, and determines syllables and rhyme types.
    *   `cl_syllables`: Calculates the number of syllables in the rhyme, considering unions.
    *   `type_arte`: Determines the type of arte (major or minor) based on the number of syllables.
    *   `rhyme_types`: Determines the rhyme type based on the last word's syllables.
*   **`Poem` Class:** Represents a poem and its properties:
    *   `__init__`: Initializes a `Poem` object, classifies the poem, and determines the poem type.
    *   `rhyme_type`: Determines the type of poem based on the rhyme scheme and number of verses.
    *   `classify`: Classifies the poem by analyzing its rhymes and syllables.

The `Poem` class is the main entry point for analyzing a poem. It splits the poem into verses, analyzes each verse using the `Rhyme` class, and then determines the overall rhyme scheme and poem type.

## Examples

```python
from poem_analyser import Poem

poem_text = """
Tus ojos son luceros,
tus labios, de terciopelo,
y un amor como el que siento,
es imposible esconderlo.
"""

poem = Poem(poem_text)
print(poem.verses)
print(poem.poem_type)