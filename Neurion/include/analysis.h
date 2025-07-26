// Description: Interfaces for sequence analysis operations (GC content, codon usage, ORF finding).
#ifndef DNATOOL_ANALYSIS_H
#define DNATOOL_ANALYSIS_H

#include <string>
#include <vector>
#include <map>

namespace dnatool {

// Represents an open reading frame in an RNA sequence.
struct ORF {
    size_t start;  // Zero-based index of first base in start codon
    size_t end;    // One-past-last index (i.e., position after stop codon)
    int frame;     // Reading frame 0,1,2
};

/**
 * Calculate the GC content of a nucleotide sequence (DNA or RNA).
 * @param seq: Input sequence
 * @return Fractional GC content (0.0 to 1.0)
 */
double gcContent(const std::string& seq);

/**
 * Compute codon usage frequencies in an RNA sequence.
 * @param rna: RNA sequence of length divisible by 3
 * @return Map from codon ("AUG" etc.) to count
 * @throws std::invalid_argument if length not divisible by 3 or invalid bases
 */
std::map<std::string, size_t> codonUsage(const std::string& rna);

/**
 * Find all open reading frames (ORFs) in an RNA sequence.
 * Uses start codon AUG and stop codons UAA, UAG, UGA.
 * @param rna: RNA sequence
 * @return Vector of ORFs
 */
std::vector<ORF> findORFs(const std::string& rna);

} // namespace dnatool

#endif // DNATOOL_ANALYSIS_H
