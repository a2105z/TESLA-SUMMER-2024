// ASTA and JSON I/O operations for sequences, mutation maps, and alignments.

#ifndef DNATOOL_IO_H
#define DNATOOL_IO_H

#include <string>
#include <vector>
#include <utility>
#include <fstream>
#include "analysis.h" // for ORF if needed

// Include nlohmann/json single-header (assumed to be available)
#include <nlohmann/json.hpp>

namespace dnatool {

using json = nlohmann::json;

/**
 * Read a single-sequence FASTA file.
 * @param filepath: Path to FASTA file
 * @return pair<sequence_id, sequence>
 * @throws std::runtime_error on I/O or format errors
 */
std::pair<std::string, std::string> readFasta(const std::string& filepath);

/**
 * Write a single-sequence FASTA file.
 * @param filepath: Path to output file
 * @param seqId: Sequence identifier (without '>')
 * @param sequence: Nucleotide sequence
 * @throws std::runtime_error on I/O errors
 */
void writeFasta(const std::string& filepath, const std::string& seqId, const std::string& sequence);

/**
 * Represents a single mutation event for JSON serialization.
 */
struct MutationRecord {
    size_t index;
    std::string type;   // "point", "insertion", "deletion"
    char original;      // original base (for insertion, original='-')
    char mutated;       // new base (for deletion, mutated='-')
};

/**
 * Serialize a vector of MutationRecords into a JSON array.
 * @param records: Vector of MutationRecord
 * @return JSON array
 */
json serializeMutationMap(const std::vector<MutationRecord>& records);

/**
 * Represents a simple sequence alignment for JSON.
 */
struct SequenceAlignment {std::string seq1; std::string seq2; int score;};

/**
 * Serialize a SequenceAlignment into JSON.
 * @param alignment: SequenceAlignment object
 * @return JSON object
 */
json serializeAlignment(const SequenceAlignment& alignment);

/**
 * Write a JSON object to file.
 * @param filepath: Path to output file
 * @param obj: JSON object
 * @throws std::runtime_error on I/O errors
 */
void writeJson(const std::string& filepath, const json& obj);

} 

#endif 