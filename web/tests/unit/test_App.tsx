import { cleanup, render } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import { App } from "../../src/App";

afterEach(cleanup);

test("renders an empty main area", () => {
  const { container } = render(<App />);

  expect(container.innerHTML).toBe("<main></main>");
});
