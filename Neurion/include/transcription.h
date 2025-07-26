// nterfaces for DNA/RNA transcription operations.

#ifndef DNATOOL_TRANSCRIPTION_H
#define DNATOOL_TRANSCRIPTION_H

#include <string>

namespace dnatool {

/**
 * Transcribe a DNA sequence to its corresponding RNA sequence.
 * Maps: A -> U, T -> A, C -> G, G -> C
 * @param dna: Input DNA sequence (letters A, T, C, G)
 * @return RNA sequence (letters A, U, C, G)
 * @throws std::invalid_argument if dna contains invalid bases
 */
std::string transcribeDNA(const std::string& dna);

/**
 * Reverse transcribe an RNA sequence back to DNA.
 * Maps: U -> A, A -> T, C -> G, G -> C
 * @param rna: Input RNA sequence (letters A, U, C, G)
 * @return DNA sequence (letters A, T, C, G)
 * @throws std::invalid_argument if rna contains invalid bases
 */
std::string reverseTranscribe(const std::string& rna);

}

#endif