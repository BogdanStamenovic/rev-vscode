import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { CSS2DObject, CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { StraightArrow } from './arrows';

export interface PickHit {
  selId: string;
  point: THREE.Vector3;
}

// Bounding box of the solid parts only (rays, labels and helper lines excluded).
function meshBox(root: THREE.Object3D): THREE.Box3 {
  const box = new THREE.Box3();
  root.traverseVisible((o) => {
    if (o.userData.noPick || !(o as THREE.Mesh).isMesh) return;
    box.expandByObject(o);
  });
  return box;
}

export class Viewport {
  readonly scene = new THREE.Scene();
  readonly camera: THREE.PerspectiveCamera;
  /** null when WebGL cannot start (software-only GPU stacks blocklist WebGL2); the
   *  panel then shows the HTML labels (names, power, direction) without the 3D shapes. */
  readonly renderer: THREE.WebGLRenderer | null;
  readonly canvas: HTMLCanvasElement;
  readonly glError: string | null;
  readonly labels: CSS2DRenderer;
  readonly orbit: OrbitControls;
  readonly gizmo: TransformControls;
  readonly world = new THREE.Group();
  readonly labelLayer = new THREE.Group();
  private grid!: THREE.GridHelper;
  private fineGrid!: THREE.GridHelper;
  private selBox = new THREE.Box3Helper(new THREE.Box3(), 0x00b3ff);
  private selObj: THREE.Object3D | null = null;
  private raycaster = new THREE.Raycaster();
  private flyKeys = new Set<string>();
  private dark = true;
  gizmoDragging = false;

  constructor(readonly container: HTMLElement) {
    let renderer: THREE.WebGLRenderer | null = null;
    let glError: string | null = null;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
      renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    } catch (e) {
      glError = e instanceof Error ? e.message : String(e);
    }
    this.renderer = renderer;
    this.glError = glError;
    this.canvas = renderer ? renderer.domElement : document.createElement('canvas');
    container.appendChild(this.canvas);
    if (glError) {
      const note = document.createElement('div');
      note.className = 'gl-error';
      note.textContent = `3D shapes are off: WebGL could not start here (${glError}). Device labels, arrows in the labels, the Driver Hub, gamepads and the code view still work.`;
      container.appendChild(note);
    }
    this.labels = new CSS2DRenderer();
    this.labels.domElement.className = 'label-layer';
    container.appendChild(this.labels.domElement);

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.005, 60);
    this.camera.position.set(0.8, 0.8, 0.8);
    this.orbit = new OrbitControls(this.camera, this.canvas);
    this.orbit.enableDamping = true;
    this.orbit.dampingFactor = 0.15;
    this.orbit.minDistance = 0.05;
    this.orbit.maxDistance = 20;
    this.orbit.target.set(0, 0, 0);
    this.orbit.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };

    this.gizmo = new TransformControls(this.camera, this.canvas);
    this.gizmo.setSize(0.8);
    this.gizmo.addEventListener('dragging-changed', (e) => {
      this.gizmoDragging = Boolean((e as unknown as { value: boolean }).value);
      this.orbit.enabled = !this.gizmoDragging;
    });
    this.scene.add(this.gizmo.getHelper());

    this.scene.add(this.world);
    this.scene.add(this.labelLayer);
    this.selBox.visible = false;
    this.selBox.userData.noPick = true;
    this.scene.add(this.selBox);
    this.buildEnvironment();
    new ResizeObserver(() => this.resize()).observe(container);
    this.resize();
  }

  private buildEnvironment(): void {
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x404050, 1.6));
    const sun = new THREE.DirectionalLight(0xffffff, 1.8);
    sun.position.set(1.5, 3, 2);
    this.scene.add(sun);
    const env = new THREE.Group();
    env.userData.noPick = true;
    this.makeGrids(0x5a6070, 0x3a3f48);
    env.add(this.grid, this.fineGrid);
    // Robot frame marking at the origin: forward is -Z, right is +X.
    const fwd = new StraightArrow(0x2ca02c, 0.004);
    fwd.set(new THREE.Vector3(0, 0, -1), 0.3);
    fwd.group.position.y = 0.001;
    const right = new StraightArrow(0xd62728, 0.004);
    right.set(new THREE.Vector3(1, 0, 0), 0.2);
    right.group.position.y = 0.001;
    env.add(fwd.group, right.group);
    const mk = (text: string, cls: string, pos: THREE.Vector3): void => {
      const el = document.createElement('div');
      el.className = 'floor-label ' + cls;
      el.textContent = text;
      const o = new CSS2DObject(el);
      o.position.copy(pos);
      env.add(o);
    };
    mk('FORWARD (-Z)', 'fwd', new THREE.Vector3(0, 0.005, -0.34));
    mk('RIGHT (+X)', 'right', new THREE.Vector3(0.26, 0.005, 0));
    env.traverse((o) => (o.userData.noPick = true));
    this.scene.add(env);
  }

  private makeGrids(major: number, minor: number): void {
    this.grid = new THREE.GridHelper(4, 16, major, major);
    this.fineGrid = new THREE.GridHelper(1, 20, minor, minor);
    const fm = this.fineGrid.material as THREE.Material;
    fm.transparent = true;
    fm.opacity = 0.5;
    this.fineGrid.position.y = 0.0005;
    this.grid.userData.noPick = true;
    this.fineGrid.userData.noPick = true;
  }

  setTheme(dark: boolean): void {
    this.dark = dark;
    this.scene.background = new THREE.Color(dark ? 0x1b1e23 : 0xeef0f3);
    // GridHelper bakes its colours into vertex colours, so theme changes rebuild it.
    const [a, b] = dark ? [0x5a6070, 0x3a3f48] : [0x9aa0aa, 0xc4c8cf];
    const parent = this.grid.parent!;
    parent.remove(this.grid, this.fineGrid);
    this.grid.dispose();
    this.fineGrid.dispose();
    this.makeGrids(a, b);
    parent.add(this.grid, this.fineGrid);
  }

  get isDark(): boolean {
    return this.dark;
  }

  resize(): void {
    const w = Math.max(10, this.container.clientWidth);
    const hgt = Math.max(10, this.container.clientHeight);
    this.renderer?.setSize(w, hgt, false);
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = hgt + 'px';
    this.labels.setSize(w, hgt);
    this.camera.aspect = w / hgt;
    this.camera.updateProjectionMatrix();
  }

  pick(clientX: number, clientY: number): PickHit | null {
    const r = this.canvas.getBoundingClientRect();
    const ndc = new THREE.Vector2(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
    this.raycaster.setFromCamera(ndc, this.camera);
    const hits = this.raycaster.intersectObject(this.world, true);
    for (const h of hits) {
      if (h.object.userData.noPick || !h.object.visible) continue;
      const id = h.object.userData.selId as string | undefined;
      if (id) return { selId: id, point: h.point };
    }
    return null;
  }

  select(obj: THREE.Object3D | null, mode: 'translate' | 'rotate'): void {
    this.selObj = obj;
    if (obj) {
      this.gizmo.attach(obj);
      this.gizmo.setMode(mode);
    } else {
      this.gizmo.detach();
    }
    this.selBox.visible = Boolean(obj);
  }

  setMode(mode: 'translate' | 'rotate'): void {
    this.gizmo.setMode(mode);
  }

  setSnap(on: boolean): void {
    this.gizmo.setTranslationSnap(on ? 0.005 : null);
    this.gizmo.setRotationSnap(on ? THREE.MathUtils.degToRad(15) : null);
  }

  // Frame every device, looking from the front-right and above (shafts face +Z by default).
  fitAll(): void {
    this.world.updateMatrixWorld(true);
    const box = meshBox(this.world);
    if (box.isEmpty()) return;
    const c = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3()).length();
    const dist = Math.max(0.3, (size / 2 / Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2))) * 0.95);
    this.orbit.target.copy(c);
    this.camera.position.copy(c).add(new THREE.Vector3(0.35, 0.75, 1).normalize().multiplyScalar(dist));
  }

  focusOn(p: THREE.Vector3): void {
    const offset = this.camera.position.clone().sub(this.orbit.target);
    const dist = Math.min(offset.length(), 0.6);
    offset.setLength(dist);
    this.orbit.target.copy(p);
    this.camera.position.copy(p).add(offset);
  }

  setFlyKey(code: string, down: boolean): void {
    if (down) this.flyKeys.add(code);
    else this.flyKeys.delete(code);
  }

  clearFly(): void {
    this.flyKeys.clear();
  }

  private fly(dt: number): void {
    if (!this.flyKeys.size) return;
    const k = this.flyKeys;
    const fast = k.has('ShiftLeft') || k.has('ShiftRight');
    const speed = (fast ? 1.6 : 0.5) * dt;
    const fwd = new THREE.Vector3();
    this.camera.getWorldDirection(fwd);
    const right = new THREE.Vector3().crossVectors(fwd, this.camera.up).normalize();
    const move = new THREE.Vector3();
    if (k.has('KeyW')) move.add(fwd);
    if (k.has('KeyS')) move.sub(fwd);
    if (k.has('KeyD')) move.add(right);
    if (k.has('KeyA')) move.sub(right);
    if (k.has('KeyE')) move.y += 1;
    if (k.has('KeyQ')) move.y -= 1;
    if (move.lengthSq() === 0) return;
    move.normalize().multiplyScalar(speed);
    this.camera.position.add(move);
    this.orbit.target.add(move);
  }

  render(dt: number): void {
    this.fly(dt);
    this.orbit.update();
    if (this.selObj && this.selBox.visible) {
      this.selBox.box.copy(meshBox(this.selObj));
      this.selBox.box.expandByScalar(0.004);
    }
    this.renderer?.render(this.scene, this.camera);
    this.labels.render(this.scene, this.camera);
  }

  // World-space raycast against everything pickable except `exclude`'s subtree; for sensors.
  castRay(origin: THREE.Vector3, dir: THREE.Vector3, far: number, exclude: THREE.Object3D): THREE.Intersection | null {
    this.raycaster.set(origin, dir);
    this.raycaster.near = 0;
    this.raycaster.far = far;
    const hits = this.raycaster.intersectObject(this.world, true);
    this.raycaster.far = Infinity;
    for (const h of hits) {
      if (h.object.userData.noPick || !h.object.visible) continue;
      let o: THREE.Object3D | null = h.object;
      let own = false;
      while (o) {
        if (o === exclude) {
          own = true;
          break;
        }
        o = o.parent;
      }
      if (!own) return h;
    }
    return null;
  }
}
