#import <Foundation/Foundation.h>
#import <ApplicationServices/ApplicationServices.h>

int main(int argc, char **argv)
{
    NSUserDefaults *args = [NSUserDefaults standardUserDefaults];
    int posx = [args floatForKey:@"x"];
    int posy = [args floatForKey:@"y"];
    bool click = [args boolForKey:@"click"];
    
    if (click == 1)
    {
        // Left button down at posxXposy
        CGEventRef click1_down = CGEventCreateMouseEvent(NULL, kCGEventLeftMouseDown, CGPointMake(posx, posy), kCGMouseButtonLeft);
        // Left button up at posxXposy
        CGEventRef click1_up = CGEventCreateMouseEvent(NULL, kCGEventLeftMouseUp, CGPointMake(posx, posy), kCGMouseButtonLeft);
        
        CGEventPost(kCGHIDEventTap, click1_down);
        CGEventPost(kCGHIDEventTap, click1_up);
        CFRelease(click1_down);
        CFRelease(click1_up);        
    } else {
        CGEventRef move1 = CGEventCreateMouseEvent(NULL, kCGEventMouseMoved, CGPointMake(posx, posy), kCGMouseButtonLeft );
        CGEventPost(kCGHIDEventTap, move1);
        CFRelease(move1);    
    }

}
