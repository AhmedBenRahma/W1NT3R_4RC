
class Solution {
public:
    vector<int> recoverOrder(vector<int>& order, vector<int>& friends) {
         vector<bool> is_friend(order.size() + 1, false);
         for (int f : friends){
            is_friend[f]=true;
         }
         vector<int> result;
        for (int id : order) {
            if (is_friend[id]) {
                result.push_back(id);
            }
        }
        
        return result;
    }
};
