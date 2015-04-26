//
//  ColorPickerViewController.m
//  ColorPicker
//
//  Created by Gilly Dekel on 23/3/09.
//  Extended by Fabián Cañas August 2010.
//  Copyright 2010. All rights reserved.
//

#import "ColorPickerViewController.h"
#import "ColorPickerView.h"
#import "UIColor-HSVAdditions.h"

@implementation ColorPickerViewController

@synthesize delegate, chooseButton;
#ifdef IPHONE_COLOR_PICKER_SAVE_DEFAULT
@synthesize defaultsKey;
#else
@synthesize defaultsColor;
#endif
@synthesize node = _node;

NSString *keyForHue = @"hue";
NSString *keyForSat = @"sat";
NSString *keyForBright = @"bright";

// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad {
    [super viewDidLoad];
#ifdef IPHONE_COLOR_PICKER_SAVE_DEFAULT
	NSUserDefaults *saveColors = [NSUserDefaults standardUserDefaults];
	if (defaultsKey==nil) {
        self.defaultsKey = @"";
        NSLog(@"problem 0 in ColorPickerViewController.viewDidLoad");
    }
    
    NSData *colorData= [saveColors objectForKey:defaultsKey];
    UIColor *color;
    if (colorData!=nil) {
        color = (UIColor*)[NSKeyedUnarchiver unarchiveObjectWithData:colorData];
    }
#endif
    
    [self moveToDefault];   // Move the crosshair to the default setting
    _node = 1;
}

-(void) moveToDefault {
  ColorPickerView *theView = (ColorPickerView*) [self view];
  #ifdef IPHONE_COLOR_PICKER_SAVE_DEFAULT
    NSUserDefaults *saveColors = [NSUserDefaults standardUserDefaults];
    NSData *colorData= [saveColors objectForKey:defaultsKey];
    UIColor *color;
    if (colorData!=nil) {
        color = (UIColor*)[NSKeyedUnarchiver unarchiveObjectWithData:colorData];
    }
    [theView setColor:color];
  #else
    [theView setColor:defaultsColor];
  #endif
}

//- (void) viewWillDisappear :(BOOL)animated { 
//
//}

- (UIColor *) getSelectedColor {
	return [(ColorPickerView *) [self view] getColorShown];
}

- (IBAction) chooseSelectedColor {
    [delegate colorPickerViewController:self didSelectColor:[self getSelectedColor]];
}

- (IBAction) cancelColorSelection {
  UIColor *color = [UIColor colorWithRGBHex:0];
//    #ifdef IPHONE_COLOR_PICKER_SAVE_DEFAULT
//    NSUserDefaults *userDefaults = [NSUserDefaults standardUserDefaults];
//
//	if (defaultsKey==nil) {
//        defaultsKey = @"";
//        NSLog(@"problem 0 in ColorPickerViewController.viewDidLoad");
//    }
//    
//    NSData *colorData= [userDefaults objectForKey:defaultsKey];
//    
//    if (colorData!=nil) {
//        color = (UIColor*)[NSKeyedUnarchiver unarchiveObjectWithData:colorData];
//    }
//    
//    #else
//    [self dismissModalViewControllerAnimated:YES];
//    #endif
  [delegate colorPickerViewController:self didTouchColor:color];
  [(ColorPickerView *) [self view] setColor:color];
}

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event {
    [delegate colorPickerViewController:self didTouchColor:[self getSelectedColor]];
}

- (void)touchesMoved:(NSSet *)touches withEvent:(UIEvent *)event {
    [delegate colorPickerViewController:self didTouchColor:[self getSelectedColor]];
}
- (IBAction)valueChosen:(id)sender {
    _node = [(UISegmentedControl *)sender selectedSegmentIndex] + 1;
    [delegate colorPickerViewController:self didSelectValue:_node];
}

- (IBAction) randomizeSelection {
    [delegate colorPickerViewControllerRandom:self];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning]; // Releases the view if it doesn't have a superview
    // Release anything that's not essential, such as cached data
}


// Housekeeping actions when a view as unloaded
- (void)viewDidUnload {
    [super viewDidUnload];
  // Release any retained subviews of the main view.
#if ___IPHONE_OS_VERSION_MAX_ALLOWED >= 30000
  [super viewDidUnload];  // First super, from iOS 3 on

  self.chooseButton=nil;   // Same as release, but also setting it to nil
#endif

  return;
}




@end
