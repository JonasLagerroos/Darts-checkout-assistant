# Darts Checkout Assistant

A Python project that recommends a checkout route for a
remaining score in darts.

## Features

- Generates possible checkout routes using up to three darts.
- Requires the final dart to be a double, including the bull.
- Prompts the user to input a remaining score and recommends
  a preferred legal route.
- Ranks checkout routes using a set of manually defined
  strategic preferences.
- Considers preferred finishing doubles and backup routes
  when a treble misses but the corresponding single is hit.
- Handles scores for which no checkout is available.

## Requirements

- Python 3
- No external Python packages required.

## How to run

1. Download this repository or clone it to your computer.
2. Open a terminal in the project folder.
3. Run the following command:

   `python dart_checkout_assistance.py`

4. Enter your remaining score when prompted.

On some Windows installations, `py dart_checkout_assistance.py`
may be used instead of `python dart_checkout_assistance.py`.

## How it works

The program generates possible checkout routes and filters
them according to the number of darts required. It then
applies a series of decision rules to select a preferred route.

The ranking rules reflect my personal approach to darts checkouts.
Some preferences reflect common checkout conventions, while others are subjective.

Players differ in their preferred finishing doubles. For example, some prefer
double 20, whereas this program prioritises double 16. The preferences can be
adjusted by changing the order of the entries in DOUBLE_PRIORITY.

The current strategy assumes that the player has three darts available and
that the opponent has a checkout available.
This assumption affects some, but not all, recommendations.

For brevity, the terms "single" and "double" in the comments generally don't
include the 25 and BULL respectively.

## Future improvements

Potential future development includes adding checkout recommendations
when you have two darts available and accounting for whether the opponent
has a checkout available.