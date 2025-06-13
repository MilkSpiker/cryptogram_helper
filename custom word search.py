import React, { useState, useEffect } from 'react';

// A predefined list of common two-letter English words for the chained search
// NOTE: This list is now primarily for reference/validation, as the secondary search
// will use the user's provided wordList.
const TWO_LETTER_WORDS_REFERENCE = new Set([
  "am", "an", "as", "at", "be", "by", "do", "go", "he", "hi", "if", "in", "is", "it",
  "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we", "ox", "oh", "lo",
  "li", "la", "ki", "jo", "ho", "ha", "fa", "eh", "de", "da", "co", "bi", "ba", "ay",
  "aw", "ar", "al", "ah", "ad", "ab", "id", "ed", "em", "en", "er", "es", "et", "ex"
]);

// Main App component
const App = () => {
  // State to store the raw text input for the word list
  const [wordInput, setWordInput] = useState('');
  // State to store the parsed word list as an array of strings
  const [wordList, setWordList] = useState([]);
  // State to store the current letter to add to search criteria
  const [newLetter, setNewLetter] = useState('');
  // State to store the current position(s) to add to search criteria (now a string for multiple inputs)
  const [newPosition, setNewPosition] = useState('');
  // State to control the 'exclusive position' setting for the new criterion being added
  const [newExclusivePosition, setNewExclusivePosition] = useState(true); // Default to true
  // State to store the list of search criteria (letter, positions array, and exclusivePositions boolean)
  const [searchCriteria, setSearchCriteria] = useState([]);
  // State to store the desired word length for primary search
  const [wordLength, setWordLength] = useState('');
  // State for letters that must NOT be present in the word (primary exclusion)
  const [excludedLetters, setExcludedLetters] = useState('');
  // State for enabling/disabling the chained search
  const [chainedSearchEnabled, setChainedSearchEnabled] = useState(false);
  // State for the target position in the primary result word for chained search
  const [chainedSearchTargetPosition, setChainedSearchTargetPosition] = useState('');
  // New state for strictness of the target position in the primary word for chained search
  const [chainedSearchExclusiveTargetPosition, setChainedSearchExclusiveTargetPosition] = useState(true); // Default to true
  // New state for the desired word length of the secondary words in the chained search
  const [chainedSearchWordLength, setChainedSearchWordLength] = useState('');
  // New state for the position in the secondary word that must match the primary word's target letter
  const [secondaryWordMatchPosition, setSecondaryWordMatchPosition] = useState(''); // Default to empty, will validate to 1
  // State to store the words that match the search criteria (now an array of [primaryWord, secondaryWord] pairs)
  const [results, setResults] = useState([]);
  // State to manage potential error messages
  const [errorMessage, setErrorMessage] = useState('');
  // State to manage success messages (e.g., after file upload)
  const [successMessage, setSuccessMessage] = useState('');

  // Effect to parse the word input whenever it changes
  useEffect(() => {
    // Split the input text by new lines, filter out empty lines, and trim whitespace
    // Also handle comma-separated values if it's a CSV, assuming one word per cell or line
    const words = wordInput
      .split(/[\n,]+/) // Split by new line or comma
      .filter(word => word.trim() !== '')
      .map(word => word.trim().toLowerCase());
    setWordList(words);
  }, [wordInput]);

  // Handler for changes in the word list textarea
  const handleWordInputChange = (e) => {
    setWordInput(e.target.value);
  };

  // Handler for file upload
  const handleFileUpload = (e) => {
    setErrorMessage(''); // Clear any previous error messages
    setSuccessMessage(''); // Clear any previous success messages
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'text/csv') {
        setErrorMessage('Please upload a .csv file.');
        return;
      }

      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const content = event.target.result;
          setWordInput(content); // Set the content to wordInput, which triggers useEffect to parse
          setSuccessMessage(`Successfully loaded "${file.name}"!`);
        } catch (error) {
          setErrorMessage('Error reading file. Please ensure it is a valid CSV.');
          console.error('File reading error:', error);
        }
      };
      reader.onerror = () => {
        setErrorMessage('Failed to read file.');
      };
      reader.readAsText(file);
    }
  };

  // Handler for adding a new search criterion
  const handleAddCriterion = () => {
    // Validate letter input
    if (!newLetter.trim()) {
      setErrorMessage('Please enter a letter.');
      return;
    }
    if (newLetter.trim().length !== 1 || !/^[a-zA-Z]$/.test(newLetter.trim())) {
      setErrorMessage('Letter must be a single alphabet character.');
      return;
    }

    // Validate and parse position(s) input
    if (!newPosition.trim()) {
      setErrorMessage('Please enter at least one position.');
      return;
    }
    const positions = newPosition.trim().split(',').map(pos => parseInt(pos.trim(), 10));
    const invalidPositions = positions.filter(pos => isNaN(pos) || pos < 1);

    if (invalidPositions.length > 0) {
      setErrorMessage('All positions must be positive numbers separated by commas.');
      return;
    }

    // Add the new criterion to the list
    setSearchCriteria(prevCriteria => [
      ...prevCriteria,
      {
        letter: newLetter.trim().toLowerCase(),
        positions: positions,
        exclusivePositions: newExclusivePosition // Add the exclusivePositions flag
      }
    ]);
    // Clear the input fields
    setNewLetter('');
    setNewPosition('');
    setErrorMessage(''); // Clear any previous error messages
    setSuccessMessage(''); // Clear success message on new action
  };

  // Handler for removing a search criterion
  const handleRemoveCriterion = (indexToRemove) => {
    setSearchCriteria(prevCriteria =>
      prevCriteria.filter((_, index) => index !== indexToRemove)
    );
    setErrorMessage(''); // Clear any previous error messages
    setSuccessMessage(''); // Clear success message on new action
  };

  // Handler to clear all search criteria
  const handleClearAllCriteria = () => {
    setSearchCriteria([]);
    setNewLetter('');
    setNewPosition('');
    setNewExclusivePosition(true); // Reset to default
    setWordLength('');
    setExcludedLetters('');
    setChainedSearchEnabled(false);
    setChainedSearchTargetPosition('');
    setChainedSearchExclusiveTargetPosition(true); // Reset to default
    setChainedSearchWordLength(''); // Clear chained search word length
    setSecondaryWordMatchPosition(''); // Clear secondary word match position
    setResults([]);
    setErrorMessage('');
    setSuccessMessage('All search criteria cleared.');
  };

  // Handler for performing the search
  const handleSearch = () => {
    setErrorMessage(''); // Clear previous errors
    setSuccessMessage(''); // Clear success message on new action

    if (wordList.length === 0) {
      setErrorMessage('Please enter words or upload a CSV file first.');
      setResults([]);
      return;
    }

    // Parse explicitly excluded letters from primary search into a Set
    const parsedExcludedLetters = new Set(
      excludedLetters.toLowerCase().split('').filter(char => /^[a-z]$/.test(char))
    );

    // --- Stage 1 Filtering (Primary Search) ---
    const desiredPrimaryLength = parseInt(wordLength, 10);
    const filterByPrimaryLength = !isNaN(desiredPrimaryLength) && desiredPrimaryLength > 0;

    const initialFilteredWords = wordList.filter(word => {
      // 1. Check word length if specified
      if (filterByPrimaryLength && word.length !== desiredPrimaryLength) {
        return false;
      }

      // 2. Check for explicitly excluded letters (from primary input)
      for (const char of word) {
        if (parsedExcludedLetters.has(char)) {
          return false; // Word contains an explicitly excluded letter
        }
      }

      // 3. Check all letter/position criteria (primary criteria)
      return searchCriteria.every(criterion => {
        const letter = criterion.letter;
        const specifiedPositionsSet = new Set(criterion.positions);

        // Condition A: Letter must be at all specified positions (AND logic)
        const matchesAllSpecifiedPositions = criterion.positions.every(position => {
          // Adjust position for 0-indexed string
          return word[position - 1] === letter;
        });

        if (!matchesAllSpecifiedPositions) {
          return false;
        }

        // Condition B: If exclusivePositions is true, letter must NOT be in any other position
        if (criterion.exclusivePositions) {
          // Iterate through the word and check characters at positions NOT in specifiedPositions
          for (let i = 0; i < word.length; i++) {
            const currentPosition = i + 1; // 1-indexed position

            // If the current position is NOT one of the specified positions,
            // AND the character at this position is the letter, then it's an invalid match.
            if (!specifiedPositionsSet.has(currentPosition) && word[i] === letter) {
              return false; // The letter appears where it shouldn't, so this word does not match this criterion
            }
          }
        }

        return true; // If all conditions pass, this word matches this criterion
      });
    });

    // --- Stage 2 Filtering (Chained Search / Refinement) ---
    let finalCombinedResults = [];

    if (chainedSearchEnabled) {
      const targetPos = parseInt(chainedSearchTargetPosition, 10);
      const desiredSecondaryLength = parseInt(chainedSearchWordLength, 10);
      const secondaryMatchPos = parseInt(secondaryWordMatchPosition, 10);

      const isValidTargetPos = !isNaN(targetPos) && targetPos > 0;
      const isValidSecondaryLength = !isNaN(desiredSecondaryLength) && desiredSecondaryLength > 0;
      const isValidSecondaryMatchPos = !isNaN(secondaryMatchPos) && secondaryMatchPos > 0;

      if (!isValidTargetPos) {
        setErrorMessage('Please enter a valid positive number for the chained search target position in the primary word.');
        setResults([]);
        return;
      }
      if (!isValidSecondaryLength) {
        setErrorMessage('Please enter a valid positive number for the chained search word length.');
        setResults([]);
        return;
      }
      if (!isValidSecondaryMatchPos) {
        setErrorMessage('Please enter a valid positive number for the target letter position in the secondary word.');
        setResults([]);
        return;
      }

      // Filter primary results further based on chainedSearchExclusiveTargetPosition
      const primaryWordsForChainedSearch = initialFilteredWords.filter(primaryWord => {
        if (!chainedSearchExclusiveTargetPosition) {
          return true; // No strictness applied
        }

        // If strict, the letter at targetPos must NOT appear anywhere else in primaryWord
        const letterAtTarget = primaryWord[targetPos - 1];
        if (!letterAtTarget) return false; // Primary word too short for target position

        for (let i = 0; i < primaryWord.length; i++) {
          if ((i + 1) !== targetPos && primaryWord[i] === letterAtTarget) {
            return false; // Letter appears elsewhere
          }
        }
        return true;
      });


      // Collect unique letters from primary results at the target position
      const secondarySearchStartingLetters = new Set();
      primaryWordsForChainedSearch.forEach(word => {
        if (word.length >= targetPos) {
          secondarySearchStartingLetters.add(word[targetPos - 1]);
        }
      });

      if (secondarySearchStartingLetters.size === 0) {
        setErrorMessage('No primary words found (after strictness filter) with a letter at the specified chained search position.');
        setResults([]);
        return;
      }

      // Define combined exclusions for the secondary words
      // This includes explicitly excluded letters from primary search AND letters from primary search criteria
      const combinedExclusionsForSecondarySearch = new Set(parsedExcludedLetters);
      searchCriteria.forEach(criterion => {
        combinedExclusionsForSecondarySearch.add(criterion.letter);
      });

      // Perform secondary search on the *original wordList*
      const secondaryMatches = wordList.filter(secondaryWord => {
        // 1. Check length
        if (secondaryWord.length !== desiredSecondaryLength) {
          return false;
        }
        // 2. Check for combined exclusions
        for (const char of secondaryWord) {
          if (combinedExclusionsForSecondarySearch.has(char)) {
            return false; // Secondary word contains an excluded letter
          }
        }
        // 3. Check if secondary word is long enough for its match position
        if (secondaryWord.length < secondaryMatchPos) {
          return false;
        }
        // 4. Check if the letter at secondaryMatchPos matches any of the required starting letters
        if (!secondarySearchStartingLetters.has(secondaryWord[secondaryMatchPos - 1])) { // Changed index here
          return false;
        }
        return true;
      });

      // Combine primary and secondary results
      primaryWordsForChainedSearch.forEach(primaryWord => {
        const charAtTargetPos = primaryWord[targetPos - 1];
        secondaryMatches.forEach(secondaryWord => {
          if (secondaryWord[secondaryMatchPos - 1] === charAtTargetPos) { // Changed index here
            finalCombinedResults.push([primaryWord, secondaryWord]);
          }
        });
      });

      // Sort finalCombinedResults by secondary word first, then primary word
      finalCombinedResults.sort((a, b) => {
        const secondaryComparison = a[1].localeCompare(b[1]);
        if (secondaryComparison !== 0) {
          return secondaryComparison;
        }
        return a[0].localeCompare(b[0]);
      });

    } else {
      // If chained search is not enabled, just show the primary results
      finalCombinedResults = initialFilteredWords.map(word => [word]); // Wrap in array for consistent display
      // If not chained, sort primary results
      finalCombinedResults.sort((a, b) => a[0].localeCompare(b[0]));
    }

    setResults(finalCombinedResults);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 p-4 font-sans flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full max-w-4xl space-y-8">
        <h1 className="text-4xl font-extrabold text-center text-gray-800 mb-8">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
            Word Searcher
          </span>
        </h1>

        {errorMessage && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md relative" role="alert">
            <strong className="font-bold">Error! </strong>
            <span className="block sm:inline">{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-md relative" role="alert">
            <strong className="font-bold">Success! </strong>
            <span className="block sm:inline">{successMessage}</span>
          </div>
        )}

        {/* Word List Input Section */}
        <div className="space-y-4">
          <label htmlFor="word-list" className="block text-lg font-semibold text-gray-700">
            1. Enter Your Custom Word List (one word per line/comma-separated) OR Upload a CSV:
          </label>
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <input
              type="file"
              id="csv-upload"
              accept=".csv"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-purple-50 file:text-purple-700
                hover:file:bg-purple-100
                cursor-pointer"
            />
          </div>
          <textarea
            id="word-list"
            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent transition duration-200 ease-in-out resize-y min-h-[150px] text-gray-800"
            rows="10"
            value={wordInput}
            onChange={handleWordInputChange}
            placeholder="e.g.,&#x0A;apple&#x0A;banana&#x0A;grape&#x0A;orange&#x0A;apricot&#x0A;or paste CSV content here..."
          ></textarea>
          <p className="text-sm text-gray-500">
            Currently loaded words: <span className="font-medium text-blue-600">{wordList.length}</span>
          </p>
        </div>

        {/* Primary Search Criteria Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-700">
            2. Primary Search Criteria:
          </h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
              placeholder="Letter (e.g., 'a')"
              value={newLetter}
              onChange={(e) => setNewLetter(e.target.value)}
              maxLength="1"
            />
            <input
              type="text"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
              placeholder="Positions (e.g., '1,3,5')"
              value={newPosition}
              onChange={(e) => setNewPosition(e.target.value)}
            />
            <button
              onClick={handleAddCriterion}
              className="px-6 py-3 bg-blue-500 text-white font-bold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 transition duration-200 ease-in-out transform hover:scale-105"
            >
              Add Criterion
            </button>
          </div>

          {/* Exclusive Position Checkbox */}
          <div className="flex items-center mt-2">
            <input
              type="checkbox"
              id="exclusive-position"
              checked={newExclusivePosition}
              onChange={(e) => setNewExclusivePosition(e.target.checked)}
              className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <label htmlFor="exclusive-position" className="ml-2 text-gray-700">
              Letter only at specified positions (strict match)
            </label>
          </div>

          {/* Word Length Input */}
          <div className="flex flex-col sm:flex-row gap-4 mb-4 mt-4">
            <input
              type="number"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
              placeholder="Exact Word Length (optional)"
              value={wordLength}
              onChange={(e) => setWordLength(e.target.value)}
              min="1"
            />
          </div>

          {/* Excluded Letters Input */}
          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
              placeholder="Excluded Letters (e.g., 'snx')"
              value={excludedLetters}
              onChange={(e) => setExcludedLetters(e.target.value)}
            />
          </div>

          {/* Display Current Primary Criteria */}
          {searchCriteria.length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="text-md font-semibold text-blue-800 mb-2">Current Letter/Position Criteria:</h3>
              <ul className="list-disc list-inside space-y-2">
                {searchCriteria.map((criterion, index) => (
                  <li key={index} className="flex items-center justify-between text-gray-700">
                    <span>
                      Letter: '<span className="font-bold text-blue-700">{criterion.letter}</span>' at Position(s): <span className="font-bold text-blue-700">{criterion.positions.join(', ')}</span>
                      {criterion.exclusivePositions ? ' (strict)' : ' (flexible)'}
                    </span>
                    <button
                      onClick={() => handleRemoveCriterion(index)}
                      className="ml-4 text-red-500 hover:text-red-700 focus:outline-none"
                      title="Remove criterion"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm6 0a1 1 0 11-2 0v6a1 1 0 112 0V8z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
              <div className="mt-4 text-right">
                <button
                  onClick={handleClearAllCriteria}
                  className="px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg shadow-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition duration-200 ease-in-out"
                >
                  Clear All Criteria
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Chained Search Section */}
        <div className="space-y-4 p-4 bg-purple-50 rounded-xl border border-purple-200">
          <h2 className="text-lg font-semibold text-purple-800 flex items-center">
            <input
              type="checkbox"
              id="chained-search-toggle"
              checked={chainedSearchEnabled}
              onChange={(e) => setChainedSearchEnabled(e.target.checked)}
              className="h-5 w-5 text-purple-600 rounded border-gray-300 focus:ring-purple-500 mr-2"
            />
            <label htmlFor="chained-search-toggle" className="cursor-pointer">
              3. Enable Chained Search (Refine Results with Secondary Words)
            </label>
          </h2>
          {chainedSearchEnabled && (
            <div className="space-y-4 mt-2">
              <p className="text-sm text-gray-600">
                Filters primary results. The word's letter at the specified position must be the matching letter of a secondary word. Secondary words are filtered by length and cannot contain letters from primary excluded list or primary search criteria.
              </p>
              <input
                type="number"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
                placeholder="Target Position in Primary Word (e.g., '2')"
                value={chainedSearchTargetPosition}
                onChange={(e) => setChainedSearchTargetPosition(e.target.value)}
                min="1"
              />
              {/* New: Strictness for Target Position in Primary Word */}
              <div className="flex items-center mt-2">
                <input
                  type="checkbox"
                  id="chained-exclusive-position"
                  checked={chainedSearchExclusiveTargetPosition}
                  onChange={(e) => setChainedSearchExclusiveTargetPosition(e.target.checked)}
                  className="h-5 w-5 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                />
                <label htmlFor="chained-exclusive-position" className="ml-2 text-gray-700">
                  Target letter only at specified position in primary word (strict)
                </label>
              </div>

              <input
                type="number"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
                placeholder="Secondary Word Length (e.g., '2')"
                value={chainedSearchWordLength}
                onChange={(e) => setChainedSearchWordLength(e.target.value)}
                min="1"
              />
              {/* New: Target Letter Position in Secondary Word */}
              <input
                type="number"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-400 focus:border-transparent transition duration-200 ease-in-out text-gray-800"
                placeholder="Target Letter Position in Secondary Word (e.g., '1')"
                value={secondaryWordMatchPosition}
                onChange={(e) => setSecondaryWordMatchPosition(e.target.value)}
                min="1"
              />
            </div>
          )}
        </div>

        {/* Search Button */}
        <div className="text-center">
          <button
            onClick={handleSearch}
            className="px-8 py-4 bg-purple-600 text-white font-extrabold text-xl rounded-lg shadow-xl hover:bg-purple-700 focus:outline-none focus:ring-4 focus:ring-purple-400 focus:ring-offset-2 transition duration-300 ease-in-out transform hover:scale-105"
          >
            {chainedSearchEnabled ? '4. Perform Chained Search' : '3. Perform Primary Search'}
          </button>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-800">
            Search Results:
          </h2>
          {results.length > 0 ? (
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-lg text-green-800 mb-2">
                Found <span className="font-bold">{results.length}</span> matching pair(s):
              </p>
              <ul className="list-disc list-inside grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                {results.map((pair, index) => (
                  <li key={index} className="text-gray-700 text-lg font-medium">
                    {pair.join(' -> ')}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-gray-600 text-lg p-4 bg-gray-50 rounded-lg border border-gray-200">
              No words found matching the criteria, or search not yet performed.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
