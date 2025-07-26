/*
 * File: transcription.cpp
 * Description: Implementation of DNA→RNA transcription and RNA→DNA reverse transcription.
 */
#include "transcription.h"
#include <stdexcept>
#include <cctype>

namespace dnatool {

std::string transcribeDNA(const std::string& dna) {
    std::string rna;
    rna.reserve(dna.size());
    for (char c : dna) {
        char base = std::toupper(static_cast<unsigned char>(c));
        switch (base) {
            case 'A': rna.push_back('A'); break;
            case 'T': rna.push_back('U'); break;
            case 'C': rna.push_back('C'); break;
            case 'G': rna.push_back('G'); break;
            default:
                // ignore non-base characters (e.g., newline) or throw
                throw std::invalid_argument("Invalid DNA base: " + std::string(1, c));
        }
    }
    return rna;
}

std::string reverseTranscribe(const std::string& rna) {
    std::string dna;
    dna.reserve(rna.size());
    for (char c : rna) {
        char base = std::toupper(static_cast<unsigned char>(c));
        switch (base) {
            case 'A': dna.push_back('A'); break;
            case 'U': dna.push_back('T'); break;
            case 'C': dna.push_back('C'); break;
            case 'G': dna.push_back('G'); break;
            default:
                throw std::invalid_argument("Invalid RNA base: " + std::string(1, c));
        }
    }
    return dna;
}

} // namespace dnatool
