#include "config.h"
#include "types.h"
#include "debug.h"
#include "vm.h"
#ifdef NVM_USE_COMMZWAVE
#include "nvmcomm_zwave.h"
#endif
#include "avr/avr_flash.h"

#include "nvmcomm3.h"

#ifdef NVMCOMM3

uint8_t testretransmission = 0;

uint8_t nvc3_avr_reprogramming = FALSE;
uint16_t nvc3_avr_reprogramming_pos;

uint8_t nvc3_appmsg_buf[NVC3_MESSAGE_SIZE];
uint8_t nvc3_appmsg_size = 0; // 0 if the buffer is not in use (so we can receive a message), otherwise indicates the length of the received message.
uint8_t nvc3_appmsg_reply = 0;

void handle_message(address_t src, u08_t nvmcomm3_command, u08_t *payload, u08_t length);
void nvmcomm_init(void) {
#ifdef NVM_USE_COMMZWAVE
  nvmcomm_zwave_init();
  nvmcomm_zwave_setcallback(handle_message);
#endif
}

void nvmcomm_poll(void) {
#ifdef NVM_USE_COMMZWAVE
  nvmcomm_zwave_poll();
#endif
}

int nvmcomm_send(address_t dest, u08_t nvc3_command, u08_t *payload, u08_t length) {
  if (length > NVC3_MESSAGE_SIZE)
    return -2; // Message too large
  int retval = nvmcomm_zwave_send(dest, nvc3_command, payload, length, TRANSMIT_OPTION_ACK + TRANSMIT_OPTION_AUTO_ROUTE);
  if (retval==0 && nvc3_command==NVC3_CMD_APPMSG)
    nvc3_appmsg_reply = NVC3_APPMSG_WAIT_ACK;
  return retval;
}
// Private

void handle_message(address_t src, u08_t nvmcomm3_command, u08_t *payload, u08_t length) {
  u08_t response_size = 0;
  u08_t response_cmd = 0;
  uint16_t pos;

#ifdef DEBUG
  DEBUGF_COMM("Handling command "DBG8" from "DBG8", length "DBG8":\n", nvmcomm3_command, src, length);
  for (size8_t i=0; i<length; ++i) {
    DEBUGF_COMM(" "DBG8"", payload[i]);
  }
  DEBUGF_COMM("\n");
#endif
  
  switch (nvmcomm3_command) {
    case NVC3_CMD_REPRG_OPEN:
      DEBUGF_COMM("Initialise reprogramming.\n");
      nvc3_avr_reprogramming = TRUE;
      nvc3_avr_reprogramming_pos = 0;
      avr_flash_open(0x4000); // TODO: ugly hack
      DEBUGF_COMM("Going to runlevel NVM_RUNLVL_CONF.\n");
      vm_set_runlevel(NVM_RUNLVL_CONF);
      response_cmd = NVC3_CMD_REPRG_OPEN_R;
    break;
    case NVC3_CMD_REPRG_WRITE:
      pos = (((uint16_t)payload[0])<<8) + ((uint16_t)payload[1]);
      DEBUGF_COMM("Received program packet for address "DBG16", current position: "DBG16".\n", pos, nvc3_avr_reprogramming_pos);
      u08_t codelength = length - 2;
      u08_t *codepayload = payload + 2;
      if (pos == nvc3_avr_reprogramming_pos) {
        DEBUGF_COMM("Write "DBG8" bytes at position "DBG16".\n", codelength, nvc3_avr_reprogramming_pos);
				avr_flash_write(codelength, codepayload);
        nvc3_avr_reprogramming_pos += codelength;
        response_cmd = NVC3_CMD_REPRG_WRITE_R_OK;
      } else {
        DEBUGF_COMM("Positions don't match. Sending WRITE_RETRANSMIT request.");
        response_cmd = NVC3_CMD_REPRG_WRITE_R_RETRANSMIT;
        payload[0] = (uint8_t)(nvc3_avr_reprogramming_pos>>8);
        payload[1] = (uint8_t)(nvc3_avr_reprogramming_pos);
        response_size = 2;
      }
    break;
    case NVC3_CMD_REPRG_COMMIT:
      pos = (((uint16_t)payload[0])<<8) + ((uint16_t)payload[1]);
      DEBUGF_COMM("Received commit request for code up to address "DBG16", current position: "DBG16".\n", pos, nvc3_avr_reprogramming_pos);
      if (pos != nvc3_avr_reprogramming_pos) {
        DEBUGF_COMM("Positions don't match. Sending COMMIT_RETRANSMIT request.");
        response_cmd = NVC3_CMD_REPRG_COMMIT_R_RETRANSMIT;
        payload[0] = (uint8_t)(nvc3_avr_reprogramming_pos>>8);
        payload[1] = (uint8_t)(nvc3_avr_reprogramming_pos);
        response_size = 2;
      } else if (0==1) {
        // TODO: add checksum, send NVC3_CMD_REPRG_COMMIT_R_FAILED if they don't match.
        response_cmd = NVC3_CMD_REPRG_COMMIT_R_FAILED;
      } else {
        DEBUGF_COMM("Committing new code.\n");
        DEBUGF_COMM("Flushing pending writes to flash.\n");
        avr_flash_close();
        response_cmd = NVC3_CMD_REPRG_COMMIT_R_OK;
      }
    break;
    
/* TODO: turn this into EEPROM file access
    case NVC3_CMD_FOPEN:
      if (payload[0] <= NVC3_MAX_FID) {
        DEBUGF_COMM("Open file "DBG8"\n", payload[0]);
        nvc3_file_open = payload[0];
        nvc3_file_pos = 0;
      }
    break;
    case NVC3_CMD_FCLOSE:
      DEBUGF_COMM("Closing file\n");
			if (nvc3_avr_flash_open == TRUE)
				avr_flash_close();
      nvc3_file_open = 0xFF;
    break;
    case NVC3_CMD_FSEEK:
      nvc3_file_pos = ((u16_t)payload[0]<<8) + payload[1];
      DEBUGF_COMM("Seek to position "DBG16"\n", nvc3_file_pos);
    break;
    case NVC3_CMD_RDFILE:
      if (nvc3_file_open == NVC3_FILE_FIRMWARE) {
        u08_t *addr = nvmfile_get_base();
        addr += nvc3_file_pos;

        response_size = payload[0];
        if (response_size < 39) { // TODO: check for buffer size (depends on protocol)
          for (size8_t i=0; i<response_size; ++i) {
            payload[i] = nvmfile_read08(addr++);
            ++nvc3_file_pos;
          }
        }
        response_cmd = NVC3_CMD_RDFILE_R;
      }
    break;
    case NVC3_CMD_WRFILE:
      if (nvc3_file_open == NVC3_FILE_FIRMWARE) {
	 			if (nvc3_avr_flash_open == FALSE) {
					nvc3_avr_flash_open = TRUE;
					avr_flash_open(0x4000); // TODO: ugly hack
        	vm_set_runlevel(NVM_RUNLVL_CONF); // opening firmware for writing implies conf runlevel
				}
        DEBUGF_COMM("Write "DBG8" bytes at position "DBG16", address "DBG16".\n", length-1, nvc3_file_pos, nvc3_file_pos);
				avr_flash_write(length, payload);
        nvc3_file_pos += length-1;
      }
    break;
*/
    case NVC3_CMD_GETRUNLVL: 
      payload[0] = nvm_runlevel;
      response_size = 1;
      response_cmd = NVC3_CMD_GETRUNLVL_R;
    break;
    case NVC3_CMD_SETRUNLVL:
      DEBUGF_COMM("Goto runlevel "DBG8"\n", payload[0]);
      vm_set_runlevel(payload[0]);
      response_cmd = NVC3_CMD_SETRUNLVL_R;
    break;
    case NVC3_CMD_APPMSG:
      DEBUGF_COMM("Received some data intended for Java\n");
      if (nvc3_appmsg_size == 0) {
        for (size8_t i=0; i<length; ++i) {
          nvc3_appmsg_buf[i] = payload[i];
        }
        nvc3_appmsg_size = length;
        payload[0] = NVC3_APPMSG_ACK;
      } else
        payload[0] = NVC3_APPMSG_BUSY;
      response_size = 1;
      response_cmd = NVC3_CMD_APPMSG_R;
    break;
    case NVC3_CMD_APPMSG_R:
      // TODO: expose this to Java. Make ACKs optional.
      nvc3_appmsg_reply = payload[0];
    break;
  }
  if (response_cmd > 0) {
    nvmcomm_send(src, response_cmd, payload, response_size);
  }
}

#endif // NVMCOMM3
