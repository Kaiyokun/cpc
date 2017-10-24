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
int* TwoSum(int nums[], int nums_size, int target, int indices[]);

#include "gtest/gtest.h"
#include <algorithm>

namespace {

    // Tests TwoSum().

    // Tests TwoSum of unique solution
    TEST(TwoSum, UniqueSolution) {

        int nums[]     = {4, 2, 6, 7, 8, 1, 5, 9, 0, 3};
        int nums_size  = sizeof(nums) / sizeof(int);
        int target     = 17;
        int indices[2] = {0};

        TwoSum(nums, nums_size, target, indices);

        std::sort(indices, indices + sizeof(indices)/sizeof(int));

        EXPECT_EQ(4, indices[0]);
        EXPECT_EQ(7, indices[1]);
    }

    // Tests TwoSum of two solution without duplication
    TEST(TwoSum, TwoSolutionWithoutDuplication) {

        int nums[]     = {9, 14, 17, 6, 13, 23, 2, 7, 20, 15};
        int nums_size  = sizeof(nums) / sizeof(int);
        int target     = 24;
        int indices[4] = {0};

        TwoSum(nums, nums_size, target, indices);

        std::sort(indices, indices + sizeof(indices)/sizeof(int));

        EXPECT_EQ(0, indices[0]);
        EXPECT_EQ(2, indices[1]);
        EXPECT_EQ(7, indices[2]);
        EXPECT_EQ(9, indices[3]);
    }

    // Tests TwoSum of two solution with duplication
    TEST(TwoSum, TwoSolutionWithDuplication) {

        int nums[]     = {6, 9, 12, 0, 1, 13, 60, 12, 45, 100};
        int nums_size  = sizeof(nums) / sizeof(int);
        int target     = 18;
        int indices[2] = {0};

        TwoSum(nums, nums_size, target, indices);

        std::sort(indices, indices + sizeof(indices)/sizeof(int));

        EXPECT_EQ(0, indices[0]);
        if (indices[1] != 2 && indices[1] != 7)
        {
            EXPECT_EQ(2, indices[1]);
            EXPECT_EQ(7, indices[1]);
        }
    }

}  // namespace
