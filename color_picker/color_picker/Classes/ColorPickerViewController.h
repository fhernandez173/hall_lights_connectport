//
//  ColorPickerViewController.h
//  ColorPicker
//
//  Created by Gilly Dekel on 23/3/09.
//  Extended by Fabián Cañas August 2010.
//  Copyright 2010. All rights reserved.
//

#import <UIKit/UIKit.h>

@class ColorPickerViewController;

@protocol ColorPickerViewControllerDelegate <NSObject>

- (void)colorPickerViewController:(ColorPickerViewController *)colorPicker didSelectColor:(UIColor *)color;

- (void)colorPickerViewController:(ColorPickerViewController *)colorPicker didTouchColor:(UIColor *)color;

- (void)colorPickerViewControllerRandom:(ColorPickerViewController *)colorPicker;

- (void)colorPickerViewController:(ColorPickerViewController *)colorPicker didSelectValue:(NSUInteger)value;

@end

@interface ColorPickerViewController : UIViewController {
    id<ColorPickerViewControllerDelegate> __unsafe_unretained delegate;
#ifdef IPHONE_COLOR_PICKER_SAVE_DEFAULT
    NSString *defaultsKey;
#else
    UIColor *defaultsColor;
#endif
    IBOutlet UIButton *chooseButton;
}

// Use this member to update the display after the default color value
// was changed.
// This is required when e.g. the view controller is kept in memory
// and is re-used for another color value selection
// Automatically called after construction, so no need to do it here.
-(void) moveToDefault;


@property(nonatomic,unsafe_unretained)	id<ColorPickerViewControllerDelegate> delegate;
@property(nonatomic,assign) NSUInteger channel;

#ifdef IPHONE_COLOR_PICKER_SAVE_DEFAULT
  @property(readwrite,nonatomic,retain) NSString *defaultsKey;
#else
  @property(readwrite,nonatomic,strong) UIColor *defaultsColor;
#endif
@property(readwrite,nonatomic,strong) IBOutlet UIButton *chooseButton;

- (IBAction) chooseSelectedColor;
- (IBAction) cancelColorSelection;
- (IBAction) randomizeSelection;
- (IBAction) valueChosen:(id)sender;
- (UIColor *) getSelectedColor;

@end

