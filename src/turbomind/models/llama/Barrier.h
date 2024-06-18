// Copyright (c) OpenMMLab. All rights reserved.

#pragma once

#include "src/turbomind/utils/cuda_utils.h"
#include "src/turbomind/utils/logger.h"
#ifndef _MSC_VER
#include <pthread.h>
#elif __cplusplus >= 202002L
#include <barrier>
#endif

namespace turbomind {

#ifdef _MSC_VER

# if __cplusplus >= 202002L
class Barrier {
public:
    Barrier(unsigned count) : barrier_(count)
    {
        TM_LOG_INFO("Barrier(%d)", (int)count);
    }

    Barrier(const Barrier&) = delete;
    Barrier& operator=(const Barrier&) = delete;
    Barrier(Barrier&&) noexcept        = delete;
    Barrier& operator=(Barrier&&) noexcept = delete;

    void wait() 
	{
        if (count_ > 1) {
            barrier_.arrive_and_wait();
        }		
	}

    ~Barrier() {}
private:
    const int         count_;
    std::barrier      barrier_;
};
# else
class Barrier {
public:
    Barrier(unsigned count)
    {
        TM_LOG_INFO("Barrier(%d)", (int)count);
        FT_CHECK(count == 1);
    }

    Barrier(const Barrier&) = delete;
    Barrier& operator=(const Barrier&) = delete;
    Barrier(Barrier&&) noexcept        = delete;
    Barrier& operator=(Barrier&&) noexcept = delete;

    void wait() {}

    ~Barrier() {}
};
# endif

#else

class Barrier {
public:
    Barrier(unsigned count): count_(count)
    {
        if (count_ > 1) {
            pthread_barrier_init(&barrier_, nullptr, count);
        }
    }

    Barrier(const Barrier&) = delete;
    Barrier& operator=(const Barrier&) = delete;
    Barrier(Barrier&&) noexcept        = delete;
    Barrier& operator=(Barrier&&) noexcept = delete;

    void wait()
    {
        if (count_ > 1) {
            pthread_barrier_wait(&barrier_);
        }
    }

    ~Barrier()
    {
        if (count_ > 1) {
            pthread_barrier_destroy(&barrier_);
        }
    }

private:
    const int         count_;
    pthread_barrier_t barrier_{};
};

#endif

}  // namespace turbomind
