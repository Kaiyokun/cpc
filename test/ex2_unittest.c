// Return true if n is a prime number.
bool IsPrime(int n);

#include <limits.h>
#include "gtest/gtest.h"

namespace {

    // Tests IsPrime()

    // Tests negative input.
    TEST(IsPrimeTest, Negative) {
        // This test belongs to the IsPrimeTest test case.
        EXPECT_FALSE(IsPrime(-1));
        EXPECT_FALSE(IsPrime(-2));
        EXPECT_FALSE(IsPrime(INT_MIN));
    }

    // Tests some trivial cases.
    TEST(IsPrimeTest, Trivial) {

        EXPECT_FALSE(IsPrime(0));
        EXPECT_FALSE(IsPrime(1));
        EXPECT_TRUE(IsPrime(2));
        EXPECT_TRUE(IsPrime(3));
    }

    // Tests positive input.
    TEST(IsPrimeTest, Positive) {

        EXPECT_FALSE(IsPrime(4));
        EXPECT_TRUE(IsPrime(5));
        EXPECT_FALSE(IsPrime(6));
        EXPECT_TRUE(IsPrime(23));
    }

}  // namespace
