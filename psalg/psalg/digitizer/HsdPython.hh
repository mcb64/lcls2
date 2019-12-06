#ifndef HSD_EVENTHEADER_HH
#define HSD_EVENTHEADER_HH

// See Hsd.hh (the DRP version of this) for a description of the
// hsd data structure from the front-end FPGA.

#include <stdint.h>
#include <stdio.h>
#include <cinttypes>

#include "xtcdata/xtc/Dgram.hh"
#include "Stream.hh"

namespace Pds {
  namespace HSD {

    class ChannelPython {
    public:
        ChannelPython() {}
        ChannelPython(uint32_t *evtheader, uint8_t* data) :
            _evtheader(evtheader), _data(data), _sh_raw(0), _sh_fex(0)
        {
            _reset_peakiter();
            unsigned streams((evtheader[0]>>20)&0x3);
            const uint8_t* p = data;
            while(streams) {
                const StreamHeader* sh = reinterpret_cast<const StreamHeader*>(p);
                if (sh->stream_id() == 0) {
                    _sh_raw = sh;
                }
                if (sh->stream_id() == 1) {
                    _sh_fex = sh;
                }
                p += sizeof(StreamHeader)+sh->num_samples()*2;
                streams &= ~(1<<sh->stream_id());
            }
        }

        ~ChannelPython(){}

        uint16_t* waveform(unsigned& numsamples) {
            if (!_sh_raw) return 0;
            numsamples = _sh_raw->num_samples();
            uint16_t* wf = (uint16_t*)(_sh_raw+1);
            return wf;
        }

        unsigned next_peak(unsigned& startPos, uint16_t** peakPtr) {
            unsigned peakLen = 0; // indicate that, by default, we haven't found a peak
            if (!_sh_fex) return peakLen; // no more peaks to look for
            const uint16_t* q = reinterpret_cast<const uint16_t*>(_sh_fex+1);

            unsigned i;
            for(i=_startSample; i<_sh_fex->num_samples();) {
                if (q[i]&0x8000) {
                    for (unsigned j=0; j<4; j++, i++) {
                        _ns += (q[i]&0x7fff);
                    }
                    _totWidth += _width;
                    if (_in) {
                        peakLen = _width;
                        _startSample = i+1; // remember where to start for next call
                        return peakLen;
                    }
                    _width = 0;
                    _in = false;
                } else {
                    if (!_in) {
                        startPos = _ns+_totWidth;
                        *peakPtr = (uint16_t *) (q+i);
                    }
                    for (unsigned j=0; j<4; j++, i++) {
                        _width++;
                    }
                    _in = true;
                }
            }
            if (_in) {
                // I think this case happens when the last peak includes
                // the very last uint16_t in sh_fex payload.
                peakLen = _width;
            }
            // these two lines will cause the iterator to return 0
            // on the next call, ending the iteration.
            _startSample = i+1;
            _in = false;
            return peakLen;
        }
    private:
        uint32_t* _evtheader;
        uint8_t*  _data;
        const StreamHeader* _sh_raw;
        const StreamHeader* _sh_fex;

        void _reset_peakiter() {
            _ns=0;
            _in = false;
            _width = 0;
            _totWidth = 0;
            _startSample = 0;
        }

        unsigned _ns;
        bool     _in;
        unsigned _width;
        unsigned _totWidth;
        unsigned _startSample;

    };
  } // HSD
} // Pds

#endif
