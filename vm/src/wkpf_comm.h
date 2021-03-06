#ifndef WKPF_COMM_H
#define WKPF_COMM_H

#include "types.h"
#include "nvmcomm.h"

extern uint8_t wkpf_send_set_property_int16(address_t dest_node_id, uint8_t port_number, uint8_t property_number, uint16_t wuclass_id, int16_t value);
extern uint8_t wkpf_send_set_property_boolean(address_t dest_node_id, uint8_t port_number, uint8_t property_number, uint16_t wuclass_id, bool value);
extern uint8_t wkpf_send_set_property_refresh_rate(address_t dest_node_id, uint8_t port_number, uint8_t property_number, uint16_t wuclass_id, wkpf_refresh_rate_t value);
extern uint8_t wkpf_send_request_property_init(address_t dest_node_id, uint8_t port_number, uint8_t property_number);
extern void wkpf_comm_handle_message(address_t src, u08_t nvmcomm_command, u08_t *payload, u08_t *response_size, u08_t *response_cmd);

#endif // WKPF_COMM_H

