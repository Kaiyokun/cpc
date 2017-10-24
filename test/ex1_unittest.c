// Returns n! (the factorial of n).  For negative n, n! is defined to be 1.
int Factorial(int n);

#include <limits.h>
#include "gtest/gtest.h"

namespace {

    // Tests Factorial().

    // Tests factorial of negative numbers.
    TEST(FactorialTest, Negative) {
        // This test is named "Negative", and belongs to the "FactorialTest"
        // test case.
        EXPECT_EQ(1, Factorial(-5));
        EXPECT_EQ(1, Factorial(-1));
        EXPECT_GT(Factorial(-10), 0);
    }

    // Tests factorial of 0.
    TEST(FactorialTest, Zero) {

        EXPECT_EQ(1, Factorial(0));
    }

    // Tests factorial of positive numbers.
    TEST(FactorialTest, Positive) {

        EXPECT_EQ(1, Factorial(1));
        EXPECT_EQ(2, Factorial(2));
        EXPECT_EQ(6, Factorial(3));
        EXPECT_EQ(40320, Factorial(8));
    }

}  // namespace
