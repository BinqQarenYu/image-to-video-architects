import { reducer, TOAST_LIMIT } from "./use-toast"

describe("use-toast reducer", () => {
  test("ADD_TOAST adds a toast and respects TOAST_LIMIT", () => {
    const state = { toasts: [] }
    const toast = { id: "1", title: "Test Toast" }
    const action = { type: "ADD_TOAST", toast }

    const newState = reducer(state, action)

    expect(newState.toasts).toHaveLength(1)
    expect(newState.toasts[0]).toEqual(toast)

    // Test limit
    const toast2 = { id: "2", title: "Test Toast 2" }
    const stateWithLimit = reducer(newState, { type: "ADD_TOAST", toast: toast2 })
    expect(stateWithLimit.toasts).toHaveLength(TOAST_LIMIT)
    expect(stateWithLimit.toasts[0]).toEqual(toast2)
  })

  test("UPDATE_TOAST updates an existing toast", () => {
    const state = {
      toasts: [{ id: "1", title: "Old Title", open: true }]
    }
    const toast = { id: "1", title: "New Title" }
    const action = { type: "UPDATE_TOAST", toast }

    const newState = reducer(state, action)

    expect(newState.toasts[0].title).toBe("New Title")
    expect(newState.toasts[0].open).toBe(true)
  })

  test("DISMISS_TOAST sets open to false", () => {
    const state = {
      toasts: [{ id: "1", open: true }, { id: "2", open: true }]
    }

    // Test specific ID
    const newState = reducer(state, { type: "DISMISS_TOAST", toastId: "1" })
    expect(newState.toasts.find(t => t.id === "1").open).toBe(false)
    expect(newState.toasts.find(t => t.id === "2").open).toBe(true)

    // Test all
    const allDismissedState = reducer(state, { type: "DISMISS_TOAST" })
    expect(allDismissedState.toasts.every(t => t.open === false)).toBe(true)
  })

  test("REMOVE_TOAST removes a toast", () => {
    const state = {
      toasts: [{ id: "1" }, { id: "2" }]
    }

    // Test specific ID
    const newState = reducer(state, { type: "REMOVE_TOAST", toastId: "1" })
    expect(newState.toasts).toHaveLength(1)
    expect(newState.toasts.find(t => t.id === "1")).toBeUndefined()

    // Test all
    const allRemovedState = reducer(state, { type: "REMOVE_TOAST" })
    expect(allRemovedState.toasts).toHaveLength(0)
  })
})
