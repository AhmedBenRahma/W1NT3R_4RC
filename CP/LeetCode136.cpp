//1st  try High complexity 

class Solution {
public:
    int singleNumber(vector<int>& nums) {
        sort(nums.begin(),nums.end());
        for(int i=0;i<nums.size();i++){
            int frequency =count(nums.begin(), nums.end(), nums[i]);
            if (frequency==1){
                return (nums[i]);
            }
        }
        return -1;
    }
};


//2nd try  / good one operator XOR  (a xor a=0)and (a xor0 = a)

class Solution {
public:
    int singleNumber(vector<int>& nums) {
        sort(nums.begin(),nums.end());
        int res=0;
        for(int n : nums){
            res^=n;
        }
        return res;
    }
};
