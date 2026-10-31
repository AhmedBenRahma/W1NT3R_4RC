//Y4G4M1

class Solution {
public:
int reverseDigits(int num)
{
    int rev_num = 0;
    while (num > 0) {
        rev_num = rev_num * 10 + num % 10;
        num = num / 10;
    }
    return rev_num;
}
    int mirrorDistance(int n) {
        return abs( n-reverseDigits(n));
    }
};
