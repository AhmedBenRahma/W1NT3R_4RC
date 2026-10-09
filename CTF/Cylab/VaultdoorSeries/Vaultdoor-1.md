<img width="770" height="66" alt="image" src="https://github.com/user-attachments/assets/033be556-b5d7-47cb-8e65-759501b4da69" />

Java source with a password checker. Instead of comparing a string, it checks `charAt(i)` one position at a time, but the checks are shuffled so the password isn't readable top to bottom.
I just sorted the conditions by index (0 to 31) and read off the characters
<img width="567" height="566" alt="image" src="https://github.com/user-attachments/assets/9d6899da-024a-4d48-8cf8-66267fcb63e6" />


Flag: `academy{d35cr4mbl3_tH3_cH4r4cT3r5_d66e42}`
