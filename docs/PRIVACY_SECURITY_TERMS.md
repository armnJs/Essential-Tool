# OmniConvert — Privacy Policy, Security Terms & Misuse Policy

**Author & Creator**: Armaan (`armnJs`)  
**Copyright**: © 2026 Armaan. All rights reserved.  
**License**: MIT License  

---

## 🔒 1. Privacy Policy

OmniConvert is designed with a **privacy-first, local-only architecture**. 

### Key Privacy Commitments:
- **100% Local Processing**: All file format transformations (Images, Documents, Data, Audio, Archives) are processed entirely on your local machine or self-hosted server instance.
- **Zero Third-Party Telemetry**: OmniConvert contains **no external tracking scripts, google analytics, telemetry, or remote cloud logging**.
- **No Data Retention**: Uploaded files exist solely in temporary memory (`io.BytesIO`) or temporary operating system buffers during conversion and are **deleted immediately** after the binary output is delivered.
- **Zero Data Selling or Sharing**: No user files, metadata, IP addresses, or converted contents are ever collected, stored, or transmitted to third parties.

---

## 🛡️ 2. Security Terms & Safeguards

The software includes built-in security controls to protect local hosting environments:

- **Input Sanitization & Path Traversal Prevention**: File names and parameters are strictly sanitized using standard operating system utilities (`os.path.basename`) and RFC 5987 header encoding to prevent directory traversal attacks.
- **Unlimited Local Payload Processing**: Since OmniConvert runs 100% locally on your machine, file size caps have been removed, allowing unlimited local conversion of large files, videos, datasets, and archives without external server overhead.
- **Safe Parsing Engine**: Structured data files are parsed using secure routines (`yaml.safe_load()`, parameterized SQL generators, and controlled XML parsers) to prevent code injection and deserialization vulnerabilities.
- **No Remote Execution**: OmniConvert does not execute arbitrary shell commands or remote code evaluation.

---

## ⚠️ 3. Acceptable Use & Misuse Policy

By downloading, installing, running, or hosting OmniConvert, you agree to abide by the following terms regarding acceptable use:

### Allowed Use:
- Converting personal, academic, or enterprise files between supported formats.
- Self-hosting the application on local networks, Docker containers, or private servers.
- Customizing and extending format converters in compliance with the MIT License.

### Prohibited Misuse:
You **MUST NOT** use OmniConvert for any of the following unauthorized activities:
1. **Illegal Content**: Converting, hosting, or processing materials that violate applicable international, federal, state, or local laws (including copyright infringement, illegal media, CSAM, or non-consensual material).
2. **Malware & Exploit Obfuscation**: Utilizing converter engines to craft, encode, disguise, or obfuscate malware, ransomware, spyware, trojans, or exploit payloads.
3. **Infrastructure Abuse & Attacks**: Deploying automated bots to conduct Denial-of-Service (DoS/DDoS) attacks, brute-force requests, or resource exhaustion against hosted instances.
4. **Unauthorized Plagiarism**: Stripping author attribution or falsely claiming original creation of OmniConvert's codebase originally authored by **Armaan**.

---

## ⚖️ 4. Disclaimer of Liability

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHOR (**ARMAAN**) OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, LEGAL ACTIONS, DATA LOSS, FINES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE, MISUSE, OR OTHER DEALINGS IN THE SOFTWARE BY END USERS OR THIRD PARTIES.
