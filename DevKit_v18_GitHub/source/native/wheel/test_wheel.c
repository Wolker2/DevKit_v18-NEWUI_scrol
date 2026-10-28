#include <assert.h>
#include <stdio.h>
#define WHEEL_TEST
#include "devkit_wheel.c"
static HANDLE foreground=(HANDLE)10;
static U32 owner_thread=77;
static int installs,removes,next_calls,posted,last_key;
U32 GetCurrentThreadId(void){return 77;}
HANDLE GetForegroundWindow(void){return foreground;}
U32 GetWindowThreadProcessId(HANDLE w,U32*p){(void)w;(void)p;return owner_thread;}
int ScreenToClient(HANDLE w,POINT*p){(void)w;p->x-=100;p->y-=50;return 1;}
HANDLE SetWindowsHookExW(int kind,HOOKPROC proc,HANDLE module,U32 tid){
    (void)module;assert(kind==3 && proc==WheelMessage && tid==77);installs++;return (HANDLE)20;
}
int UnhookWindowsHookEx(HANDLE h){assert(h==(HANDLE)20);removes++;return 1;}
IPTR CallNextHookEx(HANDLE h,int c,UPTR r,IPTR p){(void)h;(void)c;(void)r;(void)p;next_calls++;return 123;}
int PostMessageW(HANDLE w,U32 m,UPTR k,IPTR p){assert(w==(HANDLE)10 && m==WM_KEYDOWN && p==1);posted++;last_key=(int)k;return 1;}
static MSG wheel(int delta,int client_x,int client_y){
    MSG msg={(HANDLE)10,WM_MOUSEWHEEL,(UPTR)(unsigned short)(short)delta<<16,
      (IPTR)(((unsigned)(unsigned short)(client_y+50)<<16)|(unsigned short)(client_x+100)),0,{0,0}};
    return msg;
}
int main(void){
    MSG m;
    assert(WheelEnable(730,300,1190,780));
    m=wheel(-120,800,400);assert(WheelMessage(0,1,(IPTR)&m)==123);assert(m.message==WM_KEYDOWN && m.wParam==PGDN);
    m=wheel(120,800,400);WheelMessage(0,1,(IPTR)&m);assert(m.wParam==PGUP);
    m=wheel(-60,800,400);WheelMessage(0,1,(IPTR)&m);assert(m.message==WM_NULL);
    m=wheel(-60,800,400);WheelMessage(0,1,(IPTR)&m);assert(m.wParam==PGDN);
    m=wheel(360,800,400);WheelMessage(0,1,(IPTR)&m);assert(m.wParam==PGUP && posted==2 && last_key==PGUP);
    m=wheel(-120,729,400);WheelMessage(0,1,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    m=wheel(-120,1190,400);WheelMessage(0,1,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    m=wheel(-120,800,780);WheelMessage(0,1,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    m=wheel(-120,800,400);WheelMessage(-1,1,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    m=wheel(-120,800,400);WheelMessage(0,0,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    foreground=(HANDLE)11;m=wheel(-120,800,400);WheelMessage(0,1,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    foreground=(HANDLE)10;assert(WheelDisable());
    m=wheel(-120,800,400);WheelMessage(0,1,(IPTR)&m);assert(m.message==WM_MOUSEWHEEL);
    owner_thread=78;assert(!WheelEnable(730,300,1190,780));owner_thread=77;
    assert(WheelEnable(730,300,1190,780));assert(WheelDisable());
    assert(installs==2 && removes==2 && next_calls==12);
    puts("PASS: direction, multi-notch, partial delta, bounds, foreground, removal, disable, thread scope");
    return 0;
}
