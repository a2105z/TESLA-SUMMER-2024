#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdexcept>
#include <nlohmann/json.hpp>

#include "transcription.h"
#include "translation.h"
#include "mutation.h"
#include "analysis.h"
#include "io.h"
#include "codon_opt.h"

using json = nlohmann::json;
using namespace dnatool;

// Print usage information
void printUsage() {
    std::cout
        << "dnatool: DNA/RNA utility toolkit\n\n"
        << "Usage:\n"
        << "  dnatool <command> [options]\n\n"
        << "Commands:\n"
        << "  transcribe <in.fasta> <out.fasta>\n"
        << "      Read DNA FASTA, transcribe to RNA, write RNA FASTA.\n\n"
        << "  translate <in.fasta>\n"
        << "      Read RNA FASTA, translate to protein, print to stdout.\n\n"
        << "  mutate <in.fasta> <out.json> [--num N] [--maxindel M]\n"
        << "      Read DNA FASTA, apply N random mutations (default 1),\n"
        << "      max indel size M (default 3), write mutated sequence JSON.\n\n"
        << "  analyze <in.fasta>\n"
        << "      Read RNA FASTA, print GC content, codon usage, ORFs.\n\n"
        << "  optimize <protein_sequence>\n"
        << "      Codon-optimize the given protein for E. coli, print DNA.\n\n"
        << "  help\n"
        << "      Show this help message.\n";
}

// Simple argument parser for integer options
size_t parseOption(const std::vector<std::string>& args,
                   const std::string& flag,
                   size_t defaultValue) {
    for (size_t i = 0; i + 1 < args.size(); ++i) {
        if (args[i] == flag) {
            try {
                return std::stoul(args[i + 1]);
            } catch (...) {
                throw std::runtime_error("Invalid numeric value for " + flag);
            }
        }
    }
    return defaultValue;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printUsage();
        return 1;
    }

    std::string cmd = argv[1];
    std::vector<std::string> args(argv + 2, argv + argc);

    try {
        if (cmd == "help") {
            printUsage();
            return 0;

        } else if (cmd == "transcribe") {
            if (args.size() != 2) {
                throw std::runtime_error("transcribe requires <in.fasta> <out.fasta>");
            }
            auto [id, dna] = readFasta(args[0]);
            std::string rna = transcribeDNA(dna);
            writeFasta(args[1], id + "_rna", rna);
            std::cout << "Transcribed DNA → RNA saved to " << args[1] << "\n";

        } else if (cmd == "translate") {
            if (args.size() != 1) {
                throw std::runtime_error("translate requires <in.fasta>");
            }
            auto [id, rna] = readFasta(args[0]);
            std::string protein = translateRNA(rna);
            std::cout << protein << "\n";

        } else if (cmd == "mutate") {
            if (args.size() < 2) {
                throw std::runtime_error("mutate requires <in.fasta> <out.json>");
            }
            size_t num    = parseOption(args, "--num",    1);
            size_t maxInd = parseOption(args, "--maxindel", 3);

            auto [id, dna] = readFasta(args[0]);
            simulateRandomMutations(dna, num, maxInd);

            json out;
            out["id"]      = id + "_mutated";
            out["mutated"] = dna;
            writeJson(args[1], out);

            std::cout << "Applied " << num
                      << " mutation(s), result saved to " << args[1] << "\n";

        } else if (cmd == "analyze") {
            if (args.size() != 1) {
                throw std::runtime_error("analyze requires <in.fasta>");
            }
            auto [id, rna] = readFasta(args[0]);

            double gc    = gcContent(rna);
            auto usage   = codonUsage(rna);
            auto orfs    = findORFs(rna);

            std::cout << "Analysis for sequence: " << id << "\n";
            std::cout << "  GC Content: " << (gc * 100.0) << "%\n";
            std::cout << "  Codon Usage:\n";
            for (auto& [codon, count] : usage) {
                std::cout << "    " << codon << ": " << count << "\n";
            }
            std::cout << "  ORFs found:\n";
            for (auto& o : orfs) {
                std::cout << "    Frame " << o.frame
                          << ": [" << o.start << ", " << o.end << ")\n";
            }

        } else if (cmd == "optimize") {
            if (args.size() != 1) {
                throw std::runtime_error("optimize requires <protein_sequence>");
            }
            auto table = getEColiCodonTable();
            std::string dna = optimizeCodons(args[0], table);
            std::cout << dna << "\n";

        } else {
            std::cerr << "Unknown command: " << cmd << "\n\n";
            printUsage();
            return 1;
        }

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return 2;
    }

    return 0;
}
