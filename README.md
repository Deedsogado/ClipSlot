# ClipSlot
Clipboard Manager 

Gives you 10 clipboard slots instead of one to store text and images. 

Compatible with Windows Clipboard History, Cut, Copy, and Paste operations put the value into the system clipboard so they are also in the clipboard history `⊞Win+V`.   

For multiple monitor setups, ClipSlot will try to open on the focused monitor. 


## How to use 
You must have [Python](https://www.python.org/downloads/) installed.
Then install these packages: 

Run main.py to start the program. 

### Cut 
In another program, select the text or image you want to cut.  
Type `CTRL+SHIFT+X` to open ClipSlot, and see previously copied values.  

> Note: At this point the value has been cut from the other program and copied into the system clipboard, but not into ClipSlot.  

Type a number `1` through `9` (or `0` for slot 10) to copy the value into that slot. Clipslot will show the new value immediately and then close the window after a short delay. 

> You can also click on the slot with your mouse cursor, but doing so loses focus from the original program. 

You can also press `ESC` to cancel and close the window without changing the slots, but the cut value will not be returned to the other program. 


### Copy 
In another program, select the text or image you want to copy.  
Type `CTRL+SHIFT+C` to open ClipSlot, and see previously copied values.  

> Note: At this point the value has been copied into the system clipboard, but not into ClipSlot.  

Type a number `1` through `9` (or `0` for slot 10) to copy the value into that slot. Clipslot will show the new value immediately and then close the window after a short delay. 

> You can also click on the slot with your mouse cursor, but doing so loses focus from the original program. 

![Image of ClipSlot CLipboard manager](https://github.com/user-attachments/assets/aca057f4-042b-4674-91e1-97769f7ef8d8)

You can also press `ESC` to cancel and close the window without changing the slots. 

### Paste 
In another program, put your cursor or caret where you want to paste a value.  
Type `CTRL+SHIFT+V` to open ClipSlot, which shows previously copied values.  
Type a number `1` through `9` (or `0` for slot 10) to paste the value from that slot into your other program. The window will close immediately.  

> Clicking on the slot with your mouse cursor to paste doesn't work because it moves the focus to ClipSlot and pastes into the slot in ClipSlot you were trying to paste from. 

You can also press `ESC` to cancel and close the window without changing the slots. 

> Note: Pasting does not remove the value from ClipSlot. 

> Info: At this point the value has been placed into the system clipboard, so you can paste it repeatedly using `CTRL+V`.


### Future Ideas
* Light mode and Dark Mode. Toggle with `M` while window is visible.
* Window is currently docked to top of screen. Allow it to dock to other edges, or be centered. 
  * Dock to top edge. `I` while window is visible. Slots spread out horizontally. (DEFAULT)
  * Dock to left edge. `J` while window is visible. Slots stacked vertically.
  * Dock to bottom edge. `K` while window is visible. Slots spread out horizontally.
  * Dock to right edge. `L` while window is visible. Slots stacked vertically.
  * Float in center of screen. `.` while window is visible. Slots spread out horizontally.
* Use arrow keys `← ↑ ↓ →` to highlight a slot and `ENTER` to select, without moving focus from other programs.
  * Empty contents of a slot with `DEL` or `BACKSPACE`.