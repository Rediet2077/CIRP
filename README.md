SOFTWARE LICENSE PROTECTION SYSTEMS AND REVERSE ENGINEERING
1. Introduction
Software license protection systems help software companies control how their applications are used. They can restrict access to software features, limit the number of users, set expiration dates, and help prevent unauthorized use.
Reverse engineering is the process of examining a compiled program to understand how it works. In software security, it can help researchers understand how applications validate licenses and how protection mechanisms operate.
This document discusses CodeMeter, Sentinel LDK, FlexNet Publisher, Reprise License Manager (RLM), and VMProtect.
2. Basic Concepts
2.1 Software
Software is a program that performs tasks on a computer. Examples include Microsoft Office, CAD software, and Steel Beasts.
2.2 Software License
A software license is permission to use a program under specific conditions. It may specify how many computers or users are permitted, which features are available, and how long the software can be used.
2.3 License Key
A license key is a code or digital credential used to activate software or obtain a license.
For example, a user may enter a license key during activation. The licensing system checks the key according to the software vendor's rules.
A license key is not necessarily the license itself. It may be used to obtain or activate the actual license.
2.4 CPU ID and Machine ID
A CPU ID contains information about a processor, but it is not always a unique identifier for an entire computer.
Some licensing systems use hardware information or a machine fingerprint to associate a license with a particular computer. A machine fingerprint may combine several system characteristics.
This can help restrict a license to an authorized device, but hardware-based identification is not the same as a license key.
2.5 License Server
A license server manages licenses for multiple computers, usually over a local network or organizational network. It can control how many users access licensed software simultaneously.
2.6 Reverse Engineering
Reverse engineering involves analyzing a compiled program to understand its structure and behavior. Tools such as Ghidra can help researchers examine executable files, functions, strings, and program instructions.
3. CodeMeter
Company: WIBU-SYSTEMS
Main purpose: Software license management and application protection.
CodeMeter helps software developers manage licenses, control access to features, and protect applications. It supports different licensing arrangements, including software-based containers, hardware dongles, and network licensing.
3.1 Important CodeMeter Components
CodeMeter Runtime: Provides licensing services used by protected applications to check the required license.
CodeMeter Control Center: A desktop application for viewing and managing local CodeMeter components and containers.
CodeMeter container: A protected environment in which CodeMeter manages license data. It may be software-based or stored in a hardware device such as a USB CmDongle.
WebDepot: A web-based activation service provided by a software vendor to help customers activate licenses.
CodeMeter Diagnostics: Helps collect technical information for troubleshooting installation and configuration problems.
3.2 How CodeMeter Works
Consider Steel Beasts as an example.
The customer purchases a license.
The vendor provides purchase information and activation instructions.
The customer activates the license through the vendor's supported process.
The license is placed in the appropriate CodeMeter container.
When the customer runs the software, the application requests a license check.
CodeMeter provides licensing services, and the application uses the result to determine whether licensed functionality can be used.
Buying a license and activating it are different steps. Purchasing provides the entitlement; activation makes the license available through the supported licensing mechanism.
3.3 CodeMeter License Arrangements
Classic: A licensing arrangement defined by the vendor's terms, often used for longer-term access.
Time-Based: A license valid for a defined period.
Software Rental: Access provided under rental terms.
The exact conditions, renewal rules, and offline capabilities depend on the vendor's configuration.
3.4 Strengths of CodeMeter
Supports software-based and hardware-based licensing.
Can control access to specific features and time-limited licenses.
Provides licensing administration and application-protection tools.
Can support offline use when the license configuration permits it.
3.5 Weaknesses of CodeMeter
Integration and configuration can be complex.
Some deployments require additional licensing components or administration.
It cannot guarantee complete protection against every form of reverse engineering or tampering.
4. Other Software Protection Systems
4.1 Sentinel LDK
Company: Thales
Main purpose: Software licensing and application protection.
Sentinel LDK helps developers create and manage software licenses and protect applications. It supports software-based licensing and hardware-based protection devices.
Strengths:
Supports different licensing and activation options.
Can control access to licensed features.
Provides application-protection tools.
Weaknesses:
Configuration and integration can require technical knowledge.
Protection depends on how the developer implements and configures the system.
Main techniques
1. Code obfuscation
Makes program code harder to understand.
For example, a clear function name like checkLicense() might be changed to a confusing name. This is a simple illustration; actual protection can be more complex.
2. Code encryption or wrapping
Some application-protection systems transform or wrap protected code so it is harder to inspect directly. The exact method depends on the protection configuration.
3. Anti-debugging
Makes it harder for someone to examine the running program using a debugger, such as the debugger in Ghidra.
4. Anti-tampering
Helps detect or prevent unauthorized changes to the protected application.

4.2 FlexNet Publisher
Company: Flexera, through its Revenera software licensing business.
Main purpose: Software license management, particularly centralized and network licensing.
FlexNet Publisher helps organizations manage licenses across computers and networks. One of its important uses is floating licensing.
Example: A university purchases five concurrent licenses for an application. Twenty students may use the application at different times, but normally only five can use those licenses simultaneously.
Strengths:
Centralized license management.
Imagine a company has 100 employees who use the same software. Instead of managing each license separately on every computer, the company can manage licenses through a central license server.
Technique: License Server Architecture
The company installs and configures a license server.
The server manages the available licenses.
Employees' computers request permission to use the software.
The server checks whether a license is available and grants or denies the request

Supports floating and network licensing.
A floating-license system allows different employees to use those 10 licenses at different times, rather than requiring 50 separate licenses.
Technique: Concurrent License Allocation
When an employee opens the software, it requests a license from the server.
If a license is available, the server grants access.
While the employee uses it, that license is occupied.
When the employee closes the software and the license is properly released, another employee can use it

Helps organizations manage license availability and usage.
The administrator needs to know how many licenses exist, how many are being used, and whether employees can access the software.
Techniques:
License checkout and check-in: Tracks when a license is allocated to a user and when it is released.
Usage monitoring and logs: Can help administrators review license usage and troubleshoot access problems.
License limits and policies: Control how many users can use the software at the same time, according to the configured license terms.

Weaknesses:
License-server setup and maintenance may require technical expertise.
Server or network problems can interrupt access to network licenses.
It is not primarily a code-obfuscation system.
How does code obfuscation work?
Developers can use several techniques:

1. Rename variables and functions
Change meaningful names like checkLicense into unclear names like _0x7a2.

2. Make the control flow confusing
Transform the order and structure of instructions so the program is harder to follow.

3. Hide strings
Store important text in encoded form and decode it when the program runs.
FlexNet Publisher can work offline in some configurations, but it depends on how the license is set up.
Two situations
1. Standalone or locally activated license
The software may work without an internet connection if its license is already activated and its configuration allows offline use.
Internet may not be required
2. Network license
The user's computer communicates with a license server. The server can be inside the company's local network, so internet access may not be needed. However, the computer generally must still reach that server.
License key
A code that may identify a license or activate software

Activation
Registering or enabling a license for use
The main algorithms and techniques
There is no single algorithm that does everything. Different algorithms solve different problems.
1. Hashing — creating a fingerprint
A hash function takes some data and produces a fixed-length result called a hash.
For example, the SHA-256 algorithm can calculate a hash for a license file.
What is it used for?
Detecting changes to data when the hash is compared against a trusted value.
Supporting digital signatures.
Checking data integrity in suitable designs.
2. Digital signatures — proving a license is genuine
This is one of the most useful techniques for your own licensing system.
A digital signature uses a pair of cryptographic keys:
Private key: Kept secret by the software vendor. It signs licenses.
Public key: Distributed with the application. It verifies signatures.
Examples of digital-signature algorithms include RSA signatures, ECDSA, and Ed25519. These are general options for your own system, not a claim about the exact algorithm used in every FlexNet configuration.
Remember: The private key must not be included in the customer application. Otherwise, an attacker who extracts it could potentially create forged licenses.

3.Encryption — keeping information secret
Encryption converts readable data into ciphertext using a cryptographic key.
For example:
Original data: Customer information
             ↓
          Encryption
             ↓
Encrypted data: Unreadable without the key
A common encryption algorithm is AES. 

4. Random number generation — creating unpredictable values
A licensing system might generate a unique license identifier or a random activation token.
For example:
ACT-7F29-84BC-103A
This example is only an illustrative identifier.
For security-sensitive tokens, use a cryptographically secure random number generator, not a simple predictable sequence such as 1001, 1002, 1003.
Remember: Randomness can help create unpredictable tokens, but it does not replace signature verification.
5. HMAC — checking data with a shared secret
HMAC is a message authentication technique that uses a secret key and a cryptographic hash function.
It helps detect changes to data when the verifier possesses the secret.
However, if you distribute the same secret inside every customer application, someone who extracts it may be able to forge valid HMACs. For licenses that must be verified by customer applications without revealing the signing secret, public-key digital signatures are often a better design.
Quick comparison
Technique
Main purpose
SHA-256
Calculate a data fingerprint
RSA, ECDSA, Ed25519 signatures
Verify authenticity and integrity
AES
Keep data confidential
Secure random generator
Generate unpredictable values
HMAC
Authenticate data using a shared secret




4.3 Reprise License Manager (RLM)
Company: Reprise Software
Main purpose: Software license management and network licensing.
RLM provides licensing tools for commercial software, including floating licenses and license-server management.
Strengths:
Supports sharing licenses across a network.
Provides license-management tools.
Can be integrated into commercial applications.
Weaknesses:
Server administration may require technical knowledge.
Network licensing depends on server availability and connectivity.
Application protection depends on the wider implementation.

4.4 VMProtect
Company: VMProtect Software
Main purpose: Code protection and anti-reverse-engineering.
VMProtect focuses on making program code more difficult to analyze and modify. It uses techniques such as code obfuscation and code virtualization.
Strengths:
Makes code analysis more difficult.
Can protect selected parts of a program.
Can complement a separate licensing system.
Weaknesses:
It is not a complete replacement for a license-management platform.
Protection may increase program complexity and affect performance.
It cannot guarantee that software will never be reverse-engineered.
5. Comparison of the Systems
System
Main purpose
Main strength
Main limitation
CodeMeter
Licensing and application protection
Flexible licensing options
Integration can be complex
Sentinel LDK
Licensing and application protection
Licensing combined with protection tools
Configuration can be complex
FlexNet Publisher
License manag
ement
Centralized and floating licensing
Server administration
RLM
License management
Network license sharing
Dependence on server availability
VMProtect
Code protection
Makes reverse engineering more difficult
Does not replace complete license management

Similarities
These systems are designed to support software security. Depending on the product, they can help control software use, protect program functionality, or make unauthorized modification more difficult.
However, they do not all serve the same purpose. CodeMeter and Sentinel LDK combine licensing and application-protection capabilities; FlexNet Publisher and RLM focus more on license management; VMProtect focuses on code protection.
6. Algorithms and Protection Techniques
An algorithm is a set of steps a computer follows to perform a task. Software protection systems may use cryptography, license-validation rules, and code-protection techniques.
The exact algorithms used depend on the product, version, and configuration. The following are important general technologies, not a verified list of algorithms used by every product in this document.
6.1 AES
AES is a symmetric encryption algorithm. It uses a secret key to encrypt and decrypt data.
Purpose: Protect the confidentiality of information.
6.2 RSA
RSA is a public-key cryptographic algorithm that can support digital signatures and encryption.
Purpose: Support security operations such as verifying signed information.
6.3 ECC
ECC stands for Elliptic Curve Cryptography. It is a family of public-key cryptographic techniques used for operations such as digital signatures and key exchange.
Purpose: Support public-key security.
6.4 SHA-256
SHA-256 is a cryptographic hash function that produces a fixed-size fingerprint of data.
Purpose: Help detect changes to data when used in an appropriate integrity-checking process.
SHA-256 is not encryption because a hash is not designed to be decrypted to recover the original data.
6.5 Digital Signatures
Digital signatures help verify that data was signed using the expected private key and that the signed content has not been changed.
Purpose: Support authenticity and integrity verification.
6.6 Code Obfuscation and Virtualization
Code obfuscation transforms code to make it more difficult to understand. Code virtualization transforms selected code into instructions executed by a special virtual machine.
Purpose: Increase the effort required to analyze or modify protected program code.
These techniques serve different purposes. Encryption protects confidentiality, hashing creates fingerprints, digital signatures support authenticity and integrity, and obfuscation makes code analysis more difficult.
7. How License Validation Works
A typical licensing process can be described as follows:
The user installs and opens the application.
The application requests a license check.
The licensing system checks the relevant license information and conditions.
The system determines whether the requested license or feature is available.
The application allows or restricts the licensed functionality based on the result.
Depending on the design, the check may involve a local licensing component, a software container, a license server, or an online activation service.
A license key, CPU ID, or machine fingerprint may play a role in some systems, but not every licensing system uses all of them.
8. Reverse-Engineering Perspective
Reverse engineering helps researchers understand how software is structured and how protection mechanisms are integrated.
Researchers can examine authorized programs or lab applications to understand:
Where a program requests a license.
How the application handles valid and invalid license results.
How functions, strings, and conditional branches relate to program behavior.
How licensing components communicate with an application or server.
Ghidra can help analyze compiled executables and inspect their functions and instructions. Learning with a self-written test program is a useful starting point before studying commercial protection systems.
9. Conclusion
Software license protection systems help developers manage permissions and protect commercial applications. CodeMeter and Sentinel LDK combine licensing with application-protection capabilities. FlexNet Publisher and RLM are especially relevant to centralized and network-based license management. VMProtect focuses on making program code harder to analyze and modify.
No system is universally the best. The appropriate choice depends on the software's licensing requirements, deployment environment, administration needs, cost, and desired protection.
From a reverse-engineering perspective, understanding these systems provides insight into how software validates licenses, controls access, and applies protection techniques. Effective security depends not only on the product selected but also on how the application is designed and the protection mechanisms are integrated.


