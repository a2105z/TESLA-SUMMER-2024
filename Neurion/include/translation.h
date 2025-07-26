// Interfaces for RNA translation operations.
#ifndef DNATOOL_TRANSLATION_H
#define DNATOOL_TRANSLATION_H

#include <string>
#include <vector>

namespace dnatool {

/**
 * Translate an RNA sequence to its corresponding amino acid sequence.
 * Uses the standard genetic code. Stop codons are represented by '*'.
 * @param rna: Input RNA sequence (letters A, U, C, G)
 * @return Amino acid sequence as a string of single-letter codes
 * @throws std::invalid_argument if rna contains invalid bases or length not divisible by 3
 */
std::string translateRNA(const std::string& rna);

} 

#endif 