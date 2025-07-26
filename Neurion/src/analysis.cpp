// Implementation of sequence analysis operations.
#include "analysis.h"
#include <stdexcept>
#include <cctype>

namespace dnatool {

double gcContent(const std::string& seq) {
    if (seq.empty()) return 0.0;
    size_t gc = 0;
    for (char c : seq) {
        char b = std::toupper(static_cast<unsigned char>(c));
        if (b == 'G' || b == 'C') ++gc;
    }
    return static_cast<double>(gc) / seq.size();
}

std::map<std::string, size_t> codonUsage(const std::string& rna) {
    size_t n = rna.size();
    if (n % 3 != 0) {
        throw std::invalid_argument("RNA length must be divisible by 3");
    }
    std::map<std::string, size_t> usage;
    for (size_t i = 0; i + 3 <= n; i += 3) {
        std::string codon;
        codon.reserve(3);
        for (size_t j = 0; j < 3; ++j) {
            char c = std::toupper(static_cast<unsigned char>(rna[i + j]));
            if (c != 'A' && c != 'U' && c != 'C' && c != 'G') {
                throw std::invalid_argument("Invalid RNA base: " + std::string(1, c));
            }
            codon.push_back(c);
        }
        ++usage[codon];
    }
    return usage;
}

std::vector<ORF> findORFs(const std::string& rna) {
    std::vector<ORF> orfs;
    const std::string startCodon = "AUG";
    const std::vector<std::string> stopCodons = {"UAA", "UAG", "UGA"};
    size_t n = rna.size();
    
    // scan each frame
    for (int frame = 0; frame < 3; ++frame) {
        for (size_t i = frame; i + 3 <= n; i += 3) {
            // check start
            std::string codon = rna.substr(i, 3);
            for (auto &ch : codon) ch = std::toupper(static_cast<unsigned char>(ch));
            if (codon == startCodon) {
                // search for stop
                for (size_t j = i + 3; j + 3 <= n; j += 3) {
                    std::string sc = rna.substr(j, 3);
                    for (auto &ch : sc) ch = std::toupper(static_cast<unsigned char>(ch));
                    if (sc == stopCodons[0] || sc == stopCodons[1] || sc == stopCodons[2]) {
                        orfs.push_back(ORF{i, j + 3, frame});
                        break;
                    }
                }
            }
        }
    }
    return orfs;
}

}