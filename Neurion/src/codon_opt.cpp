// Description: Implementation of codon optimization operations.

#include "codon_opt.h"
#include <stdexcept>
#include <cctype>

namespace dnatool {

CodonTable getEColiCodonTable() {
    // Preferred codons for E. coli (example frequencies)
    return CodonTable{
        {'A', "GCT"},  // Ala
        {'R', "CGT"},  // Arg
        {'N', "AAT"},  // Asn
        {'D', "GAT"},  // Asp
        {'C', "TGT"},  // Cys
        {'Q', "CAA"},  // Gln
        {'E', "GAA"},  // Glu
        {'G', "GGT"},  // Gly
        {'H', "CAT"},  // His
        {'I', "ATT"},  // Ile
        {'L', "CTG"},  // Leu
        {'K', "AAA"},  // Lys
        {'M', "ATG"},  // Met (start)
        {'F', "TTT"},  // Phe
        {'P', "CCT"},  // Pro
        {'S', "TCT"},  // Ser
        {'T', "ACT"},  // Thr
        {'W', "TGG"},  // Trp
        {'Y', "TAT"},  // Tyr
        {'V', "GTT"},  // Val
        {'*', "TAA"}   // Stop codon
    };
}

std::string optimizeCodons(const std::string& protein,
                           const CodonTable& table) {
    std::string dna;
    dna.reserve(protein.size() * 3);
    for (char aa : protein) {
        char up = std::toupper(static_cast<unsigned char>(aa));
        auto it = table.find(up);
        if (it == table.end()) {
            throw std::invalid_argument(std::string("Unknown amino acid: ") + aa);
        }
        dna += it->second;
    }
    return dna;
}

}
