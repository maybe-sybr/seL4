#
# Copyright 2018, Data61
# Commonwealth Scientific and Industrial Research Organisation (CSIRO)
# ABN 41 687 119 230.
#
# This software may be distributed and modified according to the terms of
# the GNU General Public License version 2. Note that NO WARRANTY is provided.
# See "LICENSE_GPLv2.txt" for details.
#
# @TAG(DATA61_GPL)
#

cmake_minimum_required(VERSION 3.7.2)

config_string(
    KernelPTLevels PT_LEVELS "Number of page \
    table levels for RISC-V depends on the mode. For example there are: \
    2, 3 and 4 levels on Sv32, Sv39, Sv48 RISC-V paging modes respectively."
    DEFAULT 3 UNDEF_DISABLED
    UNQUOTE
    DEPENDS "KernelArchRiscV"
)

config_option(
    KernelRiscVHypervisorSupport RISCV_HE
    "Build as Hypervisor. Utilise RISCV virtualisation extensions to build the kernel as a hypervisor"
    DEFAULT OFF
    DEPENDS "KernelArchRiscV"
)

config_string(
    KernelRiscVHVersion RISCV_HE_VER
    "Support for RISCV HE draft versions"
    DEFAULT 4
    DEPENDS "KernelRiscVHypervisorSupport"
    UNQUOTE
)

config_string(
    KernelRiscVNumVTimers RISCV_NUM_VTIMERS
    "The number of virtual timers multiplexing the machine-mode timer"
    DEFAULT 0
    DEPENDS "KernelArchRiscV"
    UNQUOTE
)

if(KernelSel4ArchRiscV32)
    set(KernelPTLevels 2 CACHE STRING "" FORCE)
endif()

# This is not supported on RISC-V
set(KernelHardwareDebugAPIUnsupported ON CACHE INTERNAL "")

add_sources(
    DEP "KernelArchRiscV"
    PREFIX src/arch/riscv
    CFILES
        c_traps.c
        idle.c
        api/faults.c
        api/benchmark.c
        kernel/boot.c
        kernel/thread.c
        kernel/vspace.c
        machine/capdl.c
        machine/hardware.c
        machine/registerset.c
        machine/io.c
        model/statedata.c
        object/interrupt.c
        object/objecttype.c
        object/tcb.c
        smp/ipi.c
        object/vcpu.c
    ASMFILES halt.S head.S traps.S
)

add_bf_source_old("KernelArchRiscV" "structures.bf" "include/arch/riscv" "arch/object")
