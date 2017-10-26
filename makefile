GTEST_DIR = ../../..

CPPFLAGS += -isystem $(GTEST_DIR)/include

CXXFLAGS += -Wall -Wextra -Werror -pthread -D AUTO_CHECK

TEST = $(shell basename $(shell pwd))

OBJS = $(shell ls *.c | sed 's/\.c/.o/g')

.PHONY: test clean

$(TEST): $(OBJS) $(GTEST_DIR)/gtest_main.a
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $^ -o $@

test:
	./$(TEST) --gtest_output=xml

clean:
	-rm $(TEST)
	-rm *.o

%.o: %.c
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $<
