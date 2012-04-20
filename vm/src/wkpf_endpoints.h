#ifndef WKPF_ENDPOINTSH
#define WKPF_ENDPOINTSH

#include "types.h"
#include "heap.h"
#include "wkpf_profiles.h"

// TODONR: only works if heap id 0 isn't used.
#define WKPF_IS_NATIVE_ENDPOINT(x)               (x->virtual_profile_instance_heap_id == 0)
#define WKPF_IS_VIRTUAL_ENDPOINT(x)              (x->virtual_profile_instance_heap_id != 0)

typedef struct wkpf_local_endpoint_struct {
    wkpf_profile_definition *profile;
    uint8_t port_number;
    heap_id_t virtual_profile_instance_heap_id; // Set for virtual profiles, 0 for native profiles
    bool need_to_call_update;
} wkpf_local_endpoint;

extern uint8_t wkpf_create_endpoint(uint16_t profile_id, uint8_t port_number, heap_id_t virtual_profile_instance_heap_id);
extern uint8_t wkpf_remove_endpoint(uint8_t port_number);
extern uint8_t wkpf_get_endpoint_by_port(uint8_t port_number, wkpf_local_endpoint **endpoint);
extern uint8_t wkpf_get_endpoint_by_index(uint8_t index, wkpf_local_endpoint **endpoint);
extern uint8_t wkpf_get_endpoint_by_heap_id(heap_id_t virtual_profile_instance_heap_id, wkpf_local_endpoint **endpoint);
extern uint8_t wkpf_get_number_of_endpoints();
extern void wkpf_set_need_to_call_update_for_endpoint(wkpf_local_endpoint *endpoint);
extern bool wkpf_get_next_endpoint_to_update(wkpf_local_endpoint **endpoint);
extern bool wkpf_heap_id_in_use(heap_id_t heap_id); // To prevent virtual profile objects from being garbage collected

#endif // WKPF_ENDPOINTSH
