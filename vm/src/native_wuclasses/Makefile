#
# Makefile include for NanoVM core files
#

NATIVE_WUCLASSES_DIR = $(ROOT_DIR)/vm/src/native_wuclasses
NATIVE_WUCLASSES_OBJS = \
    native_wuclasses.o \
    wuclass_generic_update.o \
    wuclass_threshold_update.o \
    wuclass_numeric_controller_update.o \
    wuclass_light_update.o \
    wuclass_light_sensor_update.o \
    GENERATED_wuclass_generic.o \
    GENERATED_wuclass_threshold.o \
    GENERATED_wuclass_numeric_controller.o \
    GENERATED_wuclass_light.o \
    GENERATED_wuclass_light_sensor.o

OBJS += $(NATIVE_WUCLASSES_OBJS)

# convert and upload a class file

%.o:$(NATIVE_WUCLASSES_DIR)/%.c Makefile
	$(CC) $(CFLAGS) -c $< -o $@

%.d:$(NATIVE_WUCLASSES_DIR)/%.c
	set -e; $(CC) -MM $(CFLAGS) $< \
	| sed 's#\($*\)\.o[ :]*#\1.o $@ : #g' > $@ ; \
	[ -s $@ ] || rm -f $@