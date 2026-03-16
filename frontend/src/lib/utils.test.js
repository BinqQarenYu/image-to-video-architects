import { cn } from "./utils";

describe("cn", () => {
  test("merges class names correctly", () => {
    expect(cn("px-2", "py-2")).toBe("px-2 py-2");
  });

  test("handles conditional classes", () => {
    expect(cn("px-2", true && "py-2", false && "mt-2")).toBe("px-2 py-2");
  });

  test("handles null and undefined", () => {
    expect(cn("px-2", null, undefined)).toBe("px-2");
  });

  test("handles objects", () => {
    expect(cn({ "bg-red-500": true, "text-white": false })).toBe("bg-red-500");
  });

  test("handles arrays", () => {
    expect(cn(["px-2", "py-2"])).toBe("px-2 py-2");
  });

  test("resolves tailwind conflicts with tailwind-merge", () => {
    // tailwind-merge should prefer the last conflicting class
    expect(cn("px-2 p-4")).toBe("p-4");
    expect(cn("text-red-500 text-blue-500")).toBe("text-blue-500");
  });

  test("handles complex combinations", () => {
    expect(
      cn(
        "base-class",
        ["array-class", { "obj-true": true, "obj-false": false }],
        null,
        "px-4 py-2",
        "p-8"
      )
    ).toBe("base-class array-class obj-true p-8");
  });
});
