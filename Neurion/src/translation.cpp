/*
 * File: translation.cpp
 * Description: Implementation of biological RNA translation operations.
 */
#include "translation.h"
#include <stdexcept>
#include <cctype>
#include <unordered_map>

namespace dnatool {

static const std::unordered_map<std::string, char> codon_table = {
    {"UUU", 'F'}, {"UUC", 'F'}, {"UUA", 'L'}, {"UUG", 'L'},
    {"UCU", 'S'}, {"UCC", 'S'}, {"UCA", 'S'}, {"UCG", 'S'},
    {"UAU", 'Y'}, {"UAC", 'Y'}, {"UAA", '*'}, {"UAG", '*'},
    {"UGU", 'C'}, {"UGC", 'C'}, {"UGA", '*'}, {"UGG", 'W'},
    {"CUU", 'L'}, {"CUC", 'L'}, {"CUA", 'L'}, {"CUG", 'L'},
    {"CCU", 'P'}, {"CCC", 'P'}, {"CCA", 'P'}, {"CCG", 'P'},
    {"CAU", 'H'}, {"CAC", 'H'}, {"CAA", 'Q'}, {"CAG", 'Q'},
    {"CGU", 'R'}, {"CGC", 'R'}, {"CGA", 'R'}, {"CGG", 'R'},
    {"AUU", 'I'}, {"AUC", 'I'}, {"AUA", 'I'}, {"AUG", 'M'},
    {"ACU", 'T'}, {"ACC", 'T'}, {"ACA", 'T'}, {"ACG", 'T'},
    {"AAU", 'N'}, {"AAC", 'N'}, {"AAA", 'K'}, {"AAG", 'K'},
    {"AGU", 'S'}, {"AGC", 'S'}, {"AGA", 'R'}, {"AGG", 'R'},
    {"GUU", 'V'}, {"GUC", 'V'}, {"GUA", 'V'}, {"GUG", 'V'},
    {"GCU", 'A'}, {"GCC", 'A'}, {"GCA", 'A'}, {"GCG", 'A'},
    {"GAU", 'D'}, {"GAC", 'D'}, {"GAA", 'E'}, {"GAG", 'E'},
    {"GGU", 'G'}, {"GGC", 'G'}, {"GGA", 'G'}, {"GGG", 'G'}
};

std::string translateRNA(const std::string& rna) {
    const std::string seq = [&]() {
        // Clean and uppercase input
        std::string tmp;
        tmp.reserve(rna.size());
        for (char ch : rna) {
            char c = std::toupper(static_cast<unsigned char>(ch));
            if (c == 'A' || c == 'U' || c == 'C' || c == 'G') tmp.push_back(c);
        }
        return tmp;
    }();

    if (seq.size() < 3) return "";

    // Find first start codon AUG
    size_t start = std::string::npos;
    for (size_t i = 0; i + 3 <= seq.size(); ++i) {
        if (seq.substr(i, 3) == "AUG") {
            start = i;
            break;
        }
    }
    if (start == std::string::npos) {
        // No start codon found
        return "";
    }

    // Translate from start until first stop codon
    std::string protein;
    for (size_t i = start; i + 3 <= seq.size(); i += 3) {
        std::string codon = seq.substr(i, 3);
        auto it = codon_table.find(codon);
        if (it == codon_table.end()) {
            throw std::invalid_argument("Unknown codon: " + codon);
        }
        char aa = it->second;
        if (aa == '*') {
            // Stop translation
            break;
        }
        protein.push_back(aa);
    }
    return protein;
}

} // namespace dnatool
