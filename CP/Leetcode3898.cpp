class Solution {
public:
    vector<int> findDegrees(vector<vector<int>>& matrix) {
        vector<int> degrees(matrix.size(), 0);
         for (size_t i = 0; i < matrix.size(); ++i) {
             for (size_t j = 0; j < matrix[i].size(); ++j) {
                degrees[i]+=matrix[i][j];
             }
         }
         return degrees;
    }
};
