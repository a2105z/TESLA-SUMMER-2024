# 🧬 Neurion

**Neurion** is a terminal-based C++ toolkit for bioinformatics, designed to work with DNA and RNA sequences. It provides utilities for transcription, translation, mutation simulation, codon optimization, and biological analysis.

---

## 📦 Features

- ✅ **Transcription**: DNA → RNA  
- ✅ **Translation**: RNA → Protein  
- ✅ **Mutation Simulation**: Apply random point/indel mutations  
- ✅ **Analysis**: GC content, codon usage, and ORF finding  
- ✅ **Codon Optimization**: Optimize protein sequence for *E. coli*  
- 🚫 No external web API or GUI needed — fully terminal-based

---

## 🔧 Requirements

- CMake ≥ 3.14  
- C++17 compiler (e.g., MSVC, GCC, Clang)  
- **nlohmann/json** (included as header-only: `include/nlohmann/json.hpp`)

> ✅ All dependencies are header-only or included. No external library installation is required.

---

## 🚀 Build Instructions

```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/dnatool.git
cd dnatool

# 2. Create build directory and configure with CMake
mkdir build && cd build
cmake ..

# 3. Build the executable
cmake --build . --config Debug

# 4. Run from the output folder
cd Debug
./dnatool help
```

> On Windows + PowerShell, use `.\dnatool.exe` instead of `./dnatool`

---

## 🧪 Usage Examples

### Transcribe DNA to RNA
```bash
./dnatool transcribe ../data/sample.fasta ../data/rna_output.fasta
```

### Translate RNA to Protein
```bash
./dnatool translate ../data/rna_output.fasta
```

### Analyze RNA
```bash
./dnatool analyze ../data/rna_output.fasta
```

### Apply Random Mutations
```bash
./dnatool mutate ../data/sample.fasta ../data/mut_output.json --num 5 --maxindel 2
```

### Optimize Protein for E. coli
```bash
./dnatool optimize MAIVMGR
```

---

## 📁 Project Structure

```
Neurion/
├─ include/              # Header files
│  └─ nlohmann/          # JSON single header
├─ src/                  # Source files
├─ data/                 # Sample input/output files
├─ build/                # Build directory (created by user)
├─ CMakeLists.txt
├─ README.md             # You are here
```

---

## 🔬 Sample Input

**data/sample.fasta**
```
>TestSequence
ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG
```

---

## 🧠 Credits

Developed by Aarav Mittal
Built using C++17 and standard libraries. Inspired by real-world molecular biology workflows.

---

## 📝 License

MIT License – free for personal, academic, and commercial use.
