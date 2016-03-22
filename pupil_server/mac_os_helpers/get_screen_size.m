#import <Foundation/Foundation.h>
#import <ApplicationServices/ApplicationServices.h>




int main()
{
	CGRect display_bounds = CGDisplayBounds ( CGMainDisplayID() );	
	NSString *width = [NSString stringWithFormat:@"%.3f", display_bounds.size.width];
	NSString *height = [NSString stringWithFormat:@"%.3f", display_bounds.size.height];
	NSString *width_height = [NSString stringWithFormat:@"%@,%@", width, height];

	printf("%s", [width_height UTF8String]);
}
