/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
 #include <numeric>
class Solution {
public:
    ListNode* insertGreatestCommonDivisors(ListNode* head) {
        if (!head || !head->next) return head;
        
        ListNode* courant = head;
        
        while (courant && courant->next) {
          
            courant->next = new ListNode(std::gcd(courant->val, courant->next->val), courant->next);
            
      
            courant = courant->next->next;
        }
        
        return head;
    }
};
