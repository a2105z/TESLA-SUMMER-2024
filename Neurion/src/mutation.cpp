// Implementation of DNA/RNA mutation simulation operations.

#include "mutation.h"
#include <stdexcept>
#include <random>
#include <algorithm>

namespace dnatool {

void pointMutation(std::string& seq, size_t pos, char newBase) {
    if (pos >= seq.size()) {
        throw std::out_of_range("Point mutation position out of range");
    }
    seq[pos] = newBase;
}

void insertion(std::string& seq, size_t pos, const std::string& ins) {
    if (pos > seq.size()) {
        throw std::out_of_range("Insertion position out of range");
    }
    seq.insert(pos, ins);
}

void deletion(std::string& seq, size_t pos, size_t length) {
    if (pos + length > seq.size()) {
        throw std::out_of_range("Deletion range out of range");
    }
    seq.erase(pos, length);
}

void simulateRandomMutations(std::string& seq, size_t numMutations, size_t maxIndelSize) {
    if (seq.empty() || numMutations == 0) {
        return;
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> typeDist(0, 2);
    std::uniform_int_distribution<int> baseDist(0, 3);
    std::uniform_int_distribution<size_t> posDist;
    std::uniform_int_distribution<size_t> indelSizeDist(1, std::max<size_t>(1, maxIndelSize));
    const std::string bases = "ATCG";

    for (size_t i = 0; i < numMutations; ++i) {
        if (seq.empty()) break;
        size_t type = typeDist(gen);
        posDist = std::uniform_int_distribution<size_t>(0, seq.size() - 1);
        size_t pos = posDist(gen);

        switch (static_cast<MutationType>(type)) {
            case MutationType::Point: {
                char newBase = bases[baseDist(gen)];
                pointMutation(seq, pos, newBase);
                break;
            }
            case MutationType::Insertion: {
                size_t len = indelSizeDist(gen);
                std::string ins;
                ins.reserve(len);
                for (size_t j = 0; j < len; ++j) {
                    ins.push_back(bases[baseDist(gen)]);
                }
                insertion(seq, pos, ins);
                break;
            }
            case MutationType::Deletion: {
                size_t len = indelSizeDist(gen);
                len = std::min(len, seq.size() - pos);
                deletion(seq, pos, len);
                break;
            }
        }
    }
}

}