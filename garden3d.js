import * as THREE from './libs/three.module.js';

const container = document.getElementById('garden3d');

if (container) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#91d5f2');
  scene.fog = new THREE.Fog('#91d5f2', 15, 35);

  const camera = new THREE.PerspectiveCamera(
    42, container.clientWidth / 350, 0.1, 100
  );
  camera.position.set(0, 8, 22);
  camera.lookAt(0, 1.5, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, 350);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xdaf2ff, 0x52613a, 2));

  const sun = new THREE.DirectionalLight(0xfff0d5, 3);
  sun.position.set(-5, 10, 7);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  scene.add(sun);

  const garden = new THREE.Group();
  scene.add(garden);

  // NOVA_LANDSCAPE: tog‘lar, uylar, favvora va gullar
  const landscape = new THREE.Group();
  garden.add(landscape);

  function scenery(geometry, color, x, y, z) {
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color, roughness: 0.9 })
    );
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    landscape.add(mesh);
    return mesh;
  }

  // Tabiiy, notekis tog‘lar
  const mountainColors = ['#718b83', '#829b91', '#9aada0'];

  for (let i = 0; i < 7; i++) {
    const h = 3.2 + (i % 3) * 0.7;
    const geometry = new THREE.ConeGeometry(
      2.1 + (i % 2) * 0.4, h, 32, 12
    );
    const pos = geometry.attributes.position;

    for (let j = 0; j < pos.count; j++) {
      const x = pos.getX(j);
      const y = pos.getY(j);
      const z = pos.getZ(j);
      const variation = 1 + 0.07 * Math.sin(x * 4 + z * 3)
                         + 0.04 * Math.cos(z * 7);
      pos.setXYZ(j, x * variation, y, z * variation);
    }

    geometry.computeVertexNormals();
    scenery(
      geometry,
        // Qorli, qoyali tog‘lar
  const mountainColors = ['#718b83', '#829b91', '#9aada0'];

  for (let i = 0; i < 7; i++) {
    const h = 4 + (i % 3) * 0.8;

    const geometry = new THREE.IcosahedronGeometry(1, 3);
    const pos = geometry.attributes.position;
    const colors = [];

    for (let j = 0; j < pos.count; j++) {
      let x = pos.getX(j);
      let y = pos.getY(j);
      let z = pos.getZ(j);

      const noise =
        1 + 0.10 * Math.sin(x * 13 + z * 9)
          + 0.06 * Math.cos(y * 17 + x * 8);

      x *= noise;
      z *= noise;
      y *= noise;

      pos.setXYZ(j, x, y, z);

      const snow = y > 0.48;
      const color = new THREE.Color(
        snow ? '#f4f7f4' : mountainColors[i % 3]
      );

      colors.push(color.r, color.g, color.b);
    }

    geometry.setAttribute(
      'color',
      new THREE.Float32BufferAttribute(colors, 3)
    );

    geometry.scale(1.8 + (i % 2) * 0.4, h / 2, 1.5);

    const mountain = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 1,
        flatShading: true
      })
    );

    mountain.position.set(-8 + i * 2.6, h / 2, -7);
    mountain.castShadow = true;
    mountain.receiveShadow = true;
    landscape.add(mountain);
  }

  // Kichik uylar
  function makeHouse(x, z, wallColor) {
    scenery(new THREE.BoxGeometry(1.8, 1.35, 1.5), wallColor,
      x, 0.68, z);
    const roof = scenery(new THREE.ConeGeometry(1.35, 1, 4),
      '#9b4935', x, 1.85, z);
    roof.rotation.y = Math.PI / 4;
    scenery(new THREE.BoxGeometry(0.35, 0.7, 0.08),
      '#68452f', x, 0.38, z + 0.79);
    for (const wx of [-0.55, 0.55]) {
      scenery(new THREE.BoxGeometry(0.3, 0.35, 0.08),
        '#9bd9ed', x + wx, 0.82, z + 0.79);
    }
  }
  makeHouse(-5.2, -2.8, '#f0dfbd');
  makeHouse(5.2, -2.8, '#e7d5b5');

  // Markaziy favvora
  scenery(new THREE.CylinderGeometry(1, 1.15, 0.22, 32),
    '#b9c6c8', 0, 0.08, -3.2);
  scenery(new THREE.CylinderGeometry(0.72, 0.8, 0.12, 32),
    '#56b9d5', 0, 0.23, -3.2);
  scenery(new THREE.CylinderGeometry(0.12, 0.2, 0.75, 16),
    '#c5d0d1', 0, 0.55, -3.2);
  scenery(new THREE.SphereGeometry(0.16, 16, 12),
    '#8bdcf0', 0, 1, -3.2);

  // Favvora atrofidagi rangli gullar
  const flowerColors = ['#ed6688', '#f5d45c', '#a77be8', '#ffffff'];
  for (let i = 0; i < 24; i++) {
    const a = i * Math.PI * 2 / 24;
    const x = Math.cos(a) * 2;
    const z = -3.2 + Math.sin(a) * 2;
    scenery(new THREE.SphereGeometry(0.13, 10, 8),
      flowerColors[i % 4], x, 0.28, z);
    scenery(new THREE.CylinderGeometry(0.025, 0.035, 0.35, 6),
      '#397b3d', x, 0.12, z);
  }


  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(16, 120),
    new THREE.MeshStandardMaterial({
      color: '#568d42',
      roughness: 1
    })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.08;
  ground.receiveShadow = true;
  garden.add(ground);

  const bark = new THREE.MeshStandardMaterial({
    color: '#65432d',
    roughness: 1
  });

  const leafColors = ['#286b32', '#347f38', '#438d40', '#559b49'];
  const leafMaterials = leafColors.map(color =>
    new THREE.MeshStandardMaterial({
      color,
      roughness: 0.9
    })
  );

  const leafShape = new THREE.IcosahedronGeometry(0.25, 1);
  const fruitShape = new THREE.SphereGeometry(0.12, 16, 12);

  function addBranch(group, start, end, radius) {
    const direction = new THREE.Vector3().subVectors(end, start);
    const length = direction.length();

    const mesh = new THREE.Mesh(
      new THREE.CylinderGeometry(
        radius * 0.45, radius, length, 8
      ),
      bark
    );

    mesh.position.copy(start).add(end).multiplyScalar(0.5);
    mesh.quaternion.setFromUnitVectors(
      new THREE.Vector3(0, 1, 0),
      direction.normalize()
    );
    mesh.castShadow = true;
    group.add(mesh);
  }

  function makeTree(t, index) {
    const tree = new THREE.Group();
    const growth = Math.max(0.1, t.growth || 0.1);
    const size = t.size * (0.65 + growth * 0.5);

    const height = 2.5 * size;
    const base = new THREE.Vector3(0, 0, 0);
    const top = new THREE.Vector3(0.12 * size, height, 0);

    // Tabiiy, biroz egri daraxt tanasi
    let previous = base.clone();

    for (let i = 1; i <= 7; i++) {
      const p = new THREE.Vector3(
        Math.sin(i * 0.35) * 0.12 * size,
        height * i / 7,
        Math.cos(i * 0.3) * 0.07 * size
      );

      addBranch(tree, previous, p, (0.16 - i * 0.012) * size);
      previous = p;
    }

    // Asosiy shoxlar
    const branchTips = [];

    for (let i = 0; i < 9; i++) {
      const angle = i * Math.PI * 2 / 9;
      const h = (0.48 + (i % 4) * 0.13) * height;

      const start = new THREE.Vector3(
        0, h, 0
      );

      const end = new THREE.Vector3(
        Math.cos(angle) * (0.75 + (i % 3) * 0.12) * size,
        h + (0.35 + (i % 3) * 0.12) * size,
        Math.sin(angle) * (0.75 + (i % 3) * 0.12) * size
      );

      addBranch(tree, start, end, 0.075 * size);
      branchTips.push(end);

      // Mayda yon shoxlar
      for (let j = 0; j < 2; j++) {
        const side = angle + (j ? 0.7 : -0.7);
        const sideEnd = end.clone().add(new THREE.Vector3(
          Math.cos(side) * 0.4 * size,
          0.18 * size,
          Math.sin(side) * 0.4 * size
        ));

        addBranch(tree, end, sideEnd, 0.035 * size);
        branchTips.push(sideEnd);
      }
    }

    // Shoxlar atrofidagi tabiiy barg to‘plamlari
    branchTips.forEach((point, i) => {
      const count = 5 + (i % 4);

      for (let j = 0; j < count; j++) {
        const angle = j * 2.4 + i;
        const radius = (0.12 + (j % 3) * 0.09) * size;

        const leaf = new THREE.Mesh(
          leafShape,
          leafMaterials[(i + j) % leafMaterials.length]
        );

        leaf.position.set(
          point.x + Math.cos(angle) * radius,
          point.y + ((j % 3) - 1) * 0.13 * size,
          point.z + Math.sin(angle) * radius
        );

        const scale = (0.65 + (j % 3) * 0.16) * size;
        leaf.scale.set(scale, scale * 0.85, scale);
        leaf.castShadow = true;
        tree.add(leaf);
      }
    });

    // Yetilgan daraxtlarda mevalar
    if (growth >= 0.85) {
      const fruitMaterial = new THREE.MeshStandardMaterial({
        color: '#d83c27',
        roughness: 0.55
      });

      for (let i = 0; i < 12; i++) {
        const angle = i * 2.4;
        const fruit = new THREE.Mesh(fruitShape, fruitMaterial);

        fruit.position.set(
          Math.cos(angle) * 0.85 * size,
          height * (0.65 + (i % 4) * 0.07),
          Math.sin(angle) * 0.85 * size
        );

        fruit.scale.setScalar(size);
        fruit.castShadow = true;
        tree.add(fruit);
      }
    }

    tree.position.set(
      (t.x - 0.5) * 20,
      0,
      (index % 3 - 1) * 1.5
    );

    garden.add(tree);
  }

  window.drawGarden3D = function () {
    garden.clear();
    garden.add(ground);
    garden.add(landscape);

    const trees = window.getGardenTrees?.() || [];
    trees.forEach(makeTree);

    renderer.render(scene, camera);
  };

  let dragging = false;
  let lastX = 0;

  renderer.domElement.addEventListener('pointerdown', e => {
    dragging = true;
    lastX = e.clientX;
    renderer.domElement.setPointerCapture(e.pointerId);
  });

  renderer.domElement.addEventListener('pointermove', e => {
    if (!dragging) return;
    garden.rotation.y += (e.clientX - lastX) * 0.009;
    lastX = e.clientX;
    renderer.render(scene, camera);
  });

  renderer.domElement.addEventListener('pointerup', () => {
    dragging = false;
  });

  renderer.domElement.addEventListener('pointercancel', () => {
    dragging = false;
  });

  renderer.domElement.addEventListener('wheel', e => {
    camera.position.z = THREE.MathUtils.clamp(
      camera.position.z + e.deltaY * 0.01, 6, 17
    );
    camera.lookAt(0, 1.5, 0);
    renderer.render(scene, camera);
  });

  function resize() {
    const width = container.clientWidth;
    if (!width) return;

    camera.aspect = width / 350;
    camera.updateProjectionMatrix();
    renderer.setSize(width, 350);
    renderer.render(scene, camera);
  }

  window.addEventListener('resize', resize);
  window.drawGarden3D();
}
