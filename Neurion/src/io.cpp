// Description: Implementation of FASTA and JSON I/O operations.

#include "io.h"

// bring in std::getline
#include <istream>        // or <iostream> if you prefer
#include <string>
#include <fstream>

// in case the alias in io.h didn't come through cleanly:
#include <nlohmann/json.hpp>

#include <stdexcept>
#include <sstream>


namespace dnatool {
    
std::pair<std::string, std::string> readFasta(const std::string& filepath) {
    std::ifstream in(filepath);
    if (!in) throw std::runtime_error("Cannot open FASTA file: " + filepath);

    std::string line;
    std::string seqId;
    std::string sequence;
    if (!std::getline(in, line))
        throw std::runtime_error("Empty FASTA file: " + filepath);
    if (line.empty() || line[0] != '>')
        throw std::runtime_error("Invalid FASTA header in file: " + filepath);
    seqId = line.substr(1);
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        if (line[0] == '>') break; // ignore additional sequences
        sequence += line;
    }
    return {seqId, sequence};
}

void writeFasta(const std::string& filepath,
                const std::string& seqId,
                const std::string& sequence) {
    std::ofstream out(filepath);
    if (!out) throw std::runtime_error("Cannot open output file: " + filepath);
    out << '>' << seqId << '\n';
    const size_t lineWidth = 80;
    for (size_t i = 0; i < sequence.size(); i += lineWidth) {
        out << sequence.substr(i, lineWidth) << '\n';
    }
}

json serializeMutationMap(const std::vector<MutationRecord>& records) {
    json arr = json::array();
    for (const auto& r : records) {
        json obj;
        obj["index"] = r.index;
        obj["type"] = r.type;
        obj["original"] = std::string(1, r.original);
        obj["mutated"] = std::string(1, r.mutated);
        arr.push_back(obj);
    }
    return arr;
}

json serializeAlignment(const SequenceAlignment& alignment) {
    json obj;
    obj["seq1"] = alignment.seq1;
    obj["seq2"] = alignment.seq2;
    obj["score"] = alignment.score;
    return obj;
}

void writeJson(const std::string& filepath, const json& obj) {
    std::ofstream out(filepath);
    if (!out) throw std::runtime_error("Cannot open JSON output file: " + filepath);
    out << obj.dump(4) << std::endl;
}

} // namespace dnatool
