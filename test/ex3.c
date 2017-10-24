/*
 * !!! ATTENTION !!!
 * If you can't read any chinese characters in this file, please select the
 * #UTF-8# encoding in your text editor's #Preferences#.
 *
 * !!! 注意 !!!
 * 不要删除原始代码中的任何部分, 只需添加代码即可
 *
 * 练习内容:
 *     给定一组整数, 返回能使其和等于指定值的两个整数的下标.
 *     你可以假设每一组输入都必定有一个解, 并且同一个整数不能使用两次.
 *
 * 示例:
 *     int nums[] = {2, 7, 11, 15};
 *     int target = 9;
 *     // 因为nums[0] + num[1] = 2 + 7 = 9
 *     // 所以返回{0, 1}
 *
 * 来源: <https://leetcode.com/problems/two-sum/description/>
 */


int* TwoSum(int nums[], int nums_size, int target, int indices[]) {
/************************** TODO: 在下方完成代码功能 **************************/

return indices;

/******************************************************************************/
}


#ifndef AUTO_CHECK /* Ignore this line. */


/******************** TODO: #include以及main函数内容可修改 ********************/

#include <stdio.h>

int main(void)
{
    int nums[]     = {2, 7, 11, 15};
    int nums_size  = sizeof(nums) / sizeof(int);
    int target     = 9;
    int indices[2] = {0};

    printf("Given nums = [ ");
    for (int i=0; i<nums_size; ++i)
    {
        printf("%d ", nums[i]);
    }
    printf("], target = %d\n", target);

    TwoSum(nums, nums_size, target, indices);

    printf("Because nums[%d] + nums[%d] = %d + %d = %d\n", indices[0],
        indices[1], nums[indices[0]], nums[indices[1]], target);
    printf("return [%d, %d]\n", indices[0], indices[1]);

    printf("Is that correct? If true, please commit your code; "
        "check your code otherwise.\n");
}

/******************************************************************************/


#endif /* Ignore this line. */
