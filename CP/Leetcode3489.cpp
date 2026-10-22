class Solution {
public:
    int reverseDegree(string s) {
    int n=s.length();int res(0);
    for (int i = 1; i < n+1; i++) {
        res+=(26-(s[i-1]-'a'))*i;
    }
    return res;
    }
};
