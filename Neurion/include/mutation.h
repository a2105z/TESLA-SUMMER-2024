// Interfaces for DNA/RNA mutation simulation operations.
#ifndef DNATOOL_MUTATION_H
#define DNATOOL_MUTATION_H

#include <string>
#include <vector>

namespace dnatool {

// Types of mutations supported 

enum class MutationType {
    Point,
    Insertion,
    Deletion
};

/**
 * Perform a point mutation on the sequence at the given position.
 * @param seq: Sequence to mutate (DNA or RNA)
 * @param pos: Zero-based index to mutate
 * @param newBase: New base character
 * @throws std::out_of_range if pos >= seq.size()
 */
void pointMutation(std::string& seq, size_t pos, char newBase);

/**
 * Insert a subsequence into the sequence at the given position.
 * @param seq: Sequence to mutate
 * @param pos: Zero-based index before which insertion occurs
 * @param ins: Subsequence to insert
 * @throws std::out_of_range if pos > seq.size()
 */
void insertion(std::string& seq, size_t pos, const std::string& ins);

/**
 * Delete a subsequence from the sequence starting at the given position.
 * @param seq: Sequence to mutate
 * @param pos: Zero-based start index for deletion
 * @param length: Number of characters to delete
 * @throws std::out_of_range if pos+length > seq.size()
 */
void deletion(std::string& seq, size_t pos, size_t length);

/**
 * Simulate a number of random mutations of various types.
 * Randomly chooses between point, insertion, and deletion.
 * @param seq: Sequence to mutate
 * @param numMutations: Total number of mutations to apply
 * @param maxIndelSize: Maximum length for insertions and deletions
 */
void simulateRandomMutations(
    std::string& seq,
    size_t numMutations,
    size_t maxIndelSize = 3
);

}

#endif