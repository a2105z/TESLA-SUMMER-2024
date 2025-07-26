// Description: Interfaces for codon optimization based on organism-specific preferences.

#ifndef DNATOOL_CODON_OPT_H
#define DNATOOL_CODON_OPT_H

#include <string>
#include <map>

namespace dnatool {

//  mapping from an amino acid (single-letter code) to its preferred codon (triplet).
using CodonTable = std::map<char, std::string>;

/**
 * Retrieve a default codon preference table for E. coli.
 * @return CodonTable mapping amino acid to preferred codon.
 */
CodonTable getEColiCodonTable();

/**
 * Optimize a protein sequence by converting each amino acid into its preferred codon.
 * @param protein: Amino acid sequence (single-letter codes).
 * @param table: Codon preference table mapping amino acid to codon.
 * @return Optimized DNA sequence (uses T in place of U).
 * @throws std::invalid_argument if protein contains unknown amino acids.
 */
std::string optimizeCodons(const std::string& protein,
                           const CodonTable& table);

}

#endif 